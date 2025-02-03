import { ApiProperty } from '@nestjs/swagger';
import { IsEmail, IsNotEmpty, MinLength } from 'class-validator';

export class LoginDto {
  @ApiProperty({ description: 'The email of the user' })
//   @IsEmail()
  @IsNotEmpty()
  email: string;

  @ApiProperty({ description: 'The password of the user', minLength: 6 })
  @IsNotEmpty()
  @MinLength(6)
  password: string;
}
