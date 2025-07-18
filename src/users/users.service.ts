import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { User } from 'src/users/entities/user.entity';
import { Repository } from 'typeorm';
import { CreateUserDto } from './dto/create-user.dto';

import * as bcrypt from 'bcrypt';
import { RegisterDto } from 'src/auth/dto/register.dto';

@Injectable()
export class UsersService {
  constructor(
    @InjectRepository(User)
    private readonly userRepository: Repository<User>,
  ) {}

  async createUser(registerDto: RegisterDto): Promise<boolean> {
    const { username, email, password } = registerDto;

    const user = this.userRepository.create({
      username,
      email,
      password
    });

    await this.userRepository.save(user);
    return true;
  }

  async findUserByEmail(email: string): Promise<User | null> {
    return this.userRepository.findOne({ where: { email } });
  }

  async findUserByUsername(username: string): Promise<User | null> {
    return this.userRepository.findOne({ where: { username } });
  }

  async findUserByEmailOrUsername(email: string, username: string): Promise<User | null> {
    return this.userRepository.findOne({ where: [{ email }, { username }] });
  }
}
