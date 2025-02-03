import { Module } from '@nestjs/common';
import { MediaService } from './media.service';
import { MediaController } from './media.controller';
import { TypeOrmModule } from '@nestjs/typeorm';
import { Article } from './entities/article.entity';

@Module({
  imports: [
    TypeOrmModule.forFeature([Article]),
  ],
  providers: [MediaService],
  controllers: [MediaController]
})
export class MediaModule {}
