import { Controller, Get, UseGuards, Request, Logger } from '@nestjs/common';
import { AuthGuard } from '@nestjs/passport';
import { ApiBearerAuth, ApiOperation, ApiResponse } from '@nestjs/swagger';
import { JwtAuthGuard } from 'src/auth/guards/jwt-auth.guard';

@Controller('profile')
export class ProfileController {
  private readonly logger = new Logger(ProfileController.name);

  @ApiBearerAuth()
  @UseGuards(JwtAuthGuard)
  @Get()
  getProfile(@Request() req) {
    this.logger.log(`User requested profile: ${req.user.username}`);

    return req.user;
  }
}
