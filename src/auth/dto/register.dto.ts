import { ApiProperty } from '@nestjs/swagger';
import { IsEmail, IsNotEmpty, MinLength } from 'class-validator';

export class RegisterDto {
  @ApiProperty({ example: 'user123', description: 'Username' })
  @IsNotEmpty()
  username: string;

  @ApiProperty({ example: 'user@example.com', description: 'Email' })
  @IsEmail()
  @IsNotEmpty()
  email: string;

  @ApiProperty({ example: 'password123', description: 'Password', minLength: 6 })
  @IsNotEmpty()
  @MinLength(6)
  password: string;
}
