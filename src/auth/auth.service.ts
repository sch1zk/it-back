import { Injectable, UnauthorizedException } from '@nestjs/common';
import { RegisterDto } from './dto/register.dto';
import { User } from '../users/entities/user.entity';
import * as bcrypt from 'bcrypt';
import { UsersService } from 'src/users/users.service';
import { CreateUserDto } from 'src/users/dto/create-user.dto';
import { JwtService } from '@nestjs/jwt';

@Injectable()
export class AuthService {
  
  constructor(
    private readonly usersService: UsersService,
    private readonly jwtService: JwtService
  ) {}

  async register(registerDto: RegisterDto) {

    const hashedPassword = await bcrypt.hash(registerDto.password, 10);

    const createUserDto: CreateUserDto = {
      username: registerDto.username,
      email: registerDto.email,
      password: hashedPassword,
    };

    if (!this.usersService.createUser(createUserDto)) {
      return { message: 'User with this username or email already exists' };
    }

    return { message: 'User registered successfully' };
  }

  async validateUser(email: string, password: string): Promise<User | null> {
    const user = await this.usersService.findUserByEmail(email);
    if (!user) return null;

    const isPasswordValid = await bcrypt.compare(password, user.password);
    return isPasswordValid ? user : null;
  }

  async login(
    email: string, 
    password: string
  ): Promise<{ access_token: string }> {
    const user = await this.usersService.findUserByEmail(email);

    if (!user || !(await bcrypt.compare(password, user.password))) {
      throw new UnauthorizedException();
    }

    const payload = { sub: user.id, username: user.username };
    return {
      access_token: await this.jwtService.signAsync(payload),
    };
  }
}
