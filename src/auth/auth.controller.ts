import { Body, Controller, Logger, Post, Res } from '@nestjs/common';
import { AuthService } from './auth.service';
import { RegisterDto } from './dto/register.dto';
import { LoginDto } from './dto/login.dto';
import { ApiOperation, ApiResponse, ApiTags } from '@nestjs/swagger';
import { Response } from 'express';

@ApiTags('Auth')
@Controller('auth')
export class AuthController {
  // private readonly logger = new Logger(AuthController.name);

  constructor(private readonly authService: AuthService) {}

  @ApiOperation({ summary: 'New user registration' })
  @ApiResponse({ status: 201, description: 'User registered successfully' })
  @ApiResponse({ status: 409, description: 'User with this email already exists' })
  @Post('register')
  async register(@Body() registerDto: RegisterDto): Promise<{message: string}> {
    return await this.authService.register(registerDto);
  }

  @ApiOperation({ summary: 'User login' })
  @ApiResponse({ status: 200, description: 'Succesful login' })
  @ApiResponse({ status: 401, description: 'Invalid credentials' })
  @Post('login')
  // async login(@Body() loginDto: LoginDto, @Res() res: Response): Promise<{access_token: string}> {
  async login(@Body() loginDto: LoginDto, @Res() res: Response) {
    // return await this.authService.login(loginDto);
    const { access_token } = await this.authService.login(loginDto);

    res.cookie('jwt', access_token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      maxAge: 3600000, // 1 час
    });

    return res.send({ message: 'Logged in' });
  }

  // @ApiBearerAuth()
  // @UseGuards(JwtAuthGuard)
  // @Get('profile')
  // getProfile(@Request() req) {
  //   return req.user;
  // }
}
