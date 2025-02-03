import { Controller, Get, Param, Query } from '@nestjs/common';
import { MediaService } from './media.service';
import { ApiOperation, ApiResponse } from '@nestjs/swagger';
import { ArticleDto } from './dto/article.dto';
import { ArticleListDto } from './dto/article-list.dto';

@Controller('media')
export class MediaController {
  constructor(private readonly mediaService: MediaService) {}

  @Get()
  @ApiOperation({ summary: 'Get articles with pagination' })
  @ApiResponse({ status: 200, description: 'List of articles', type: [ArticleDto] })
  async getArticles(
    @Query('page') page: number = 1,
    @Query('limit') limit: number = 10,
  ): Promise<ArticleListDto> {
    return this.mediaService.getArticles(page, limit);
  }

  @Get(':id')
  @ApiOperation({ summary: 'Get article by id' })
  @ApiResponse({ status: 200, description: 'Article', type: ArticleDto })
  async getArticleById(@Param('id') id: number): Promise<ArticleDto> {
    return this.mediaService.getArticleById(id);
  }
}
