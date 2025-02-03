import { Injectable, NotFoundException } from '@nestjs/common';
import { Article } from './entities/article.entity';
import { Repository } from 'typeorm';
import { InjectRepository } from '@nestjs/typeorm';
import { ArticleListDto } from './dto/article-list.dto';
import { PaginationMetaDto } from 'dto/pagination-meta.dto';

@Injectable()
export class MediaService {
  constructor(
    @InjectRepository(Article)
    private articleRepository: Repository<Article>,
  ) {}

  async getArticles(page: number = 1, limit: number = 10): Promise<ArticleListDto> {
    const [articles, total] = await this.articleRepository.findAndCount({
      take: limit,
      skip: (page - 1) * limit,
    });

    const meta: PaginationMetaDto = { total, page, limit };

    return { articles, meta };
  }

  async getArticleById(id: number): Promise<Article> {
    const article = await this.articleRepository.findOne({ where: { id } });;
    if (!article) {
      throw new NotFoundException(`Article with id ${id} not found`);
    }
    
    return article;
  }
  
  // async remove(id: number): Promise<void> {
  //   const article = await this.getArticleById(id);
  //   await this.articleRepository.remove(article);
  // }
}
