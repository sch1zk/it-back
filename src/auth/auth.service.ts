import { ConflictException, Injectable, UnauthorizedException } from '@nestjs/common';
import { RegisterDto } from './dto/register.dto';
import { User } from '../users/entities/user.entity';
import * as bcrypt from 'bcrypt';
import { UsersService } from 'src/users/users.service';
import { CreateUserDto } from 'src/users/dto/create-user.dto';
import { JwtService } from '@nestjs/jwt';
import { LoginDto } from './dto/login.dto';

@Injectable()
export class AuthService {
  constructor(
    private readonly usersService: UsersService,
    private readonly jwtService: JwtService
  ) {}

  async register(registerDto: RegisterDto): Promise<{ message: string }> {
    const { username, email, password } = registerDto;

    const existingUser = await this.usersService.findUserByEmailOrUsername(email, username);
    if (existingUser) {
      throw new ConflictException('User with this email or username already exists');
    }

    const hashedPassword = await bcrypt.hash(password, 10);

    await this.usersService.createUser({ ...registerDto, password: hashedPassword });

    return { message: 'User registered successfully' };
  }

  async validateUser(email: string, password: string) {
    const user = await this.usersService.findUserByEmail(email);

    if (user && (await bcrypt.compare(password, user.password))) {
      const { password: _, ...userWithoutPassword } = user;
      return userWithoutPassword;
    }

    throw new UnauthorizedException('Invalid credentials');
  }

  async login(loginDto: LoginDto): Promise<{ access_token: string }> {
    const { email, password } = loginDto;

    const user = await this.validateUser(email, password);

    const payload = { username: user.username, sub: user.id };
    const access_token = await this.jwtService.signAsync(payload);

    return { access_token };
  }
}
