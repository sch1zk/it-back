import { Injectable, Logger, NotFoundException } from '@nestjs/common';
import { Repository } from 'typeorm';
import { Profile } from './entities/profile.entity';
import { InjectRepository } from '@nestjs/typeorm';
import { User } from 'src/users/entities/user.entity';
import { UpdateProfileDto } from './dto/update-profile.dto';

@Injectable()
export class ProfileService {
  private readonly logger = new Logger(ProfileService.name);

  constructor(
    @InjectRepository(User)
    private readonly userRepository: Repository<User>,
    @InjectRepository(Profile)
    private readonly profileRepository: Repository<Profile>,
  ) {}

  async getUserProfile(userId: string): Promise<Profile> {
    const user = await this.userRepository.findOne({
      where: { id: userId },
      relations: ['profile'],
    });

    if (!user) {
      throw new NotFoundException('User not found');
    }

    if (!user.profile) {
        this.logger.log(`Profile for user ${user.id} not found, creating new...`);
        const newProfile = await this.createUserProfile(user.id);
        return newProfile;
      }

    return user.profile;
  }

  async createUserProfile(userId: string): Promise<Profile> {
    const user = await this.userRepository.findOne({ where: { id: userId } });

    if (!user) {
      throw new NotFoundException('User not found');
    }

    const profile = this.profileRepository.create({
      user,
    });

    return await this.profileRepository.save(profile);
  }

  async updateUserProfile(userId: string, profileDto: UpdateProfileDto): Promise<Profile> {
    const user = await this.userRepository.findOne({ where: { id: userId }, relations: ['profile'] });

    if (!user) {
      throw new NotFoundException('User not found');
    }

    if (!user.profile) {
      throw new NotFoundException('Profile not found');
    }

    Object.assign(user.profile, profileDto);
    return await this.profileRepository.save(user.profile);
  }
}
