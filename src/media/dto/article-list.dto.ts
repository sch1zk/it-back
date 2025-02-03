import { ArticleDto } from './article.dto';
import { PaginationMetaDto } from '../../../dto/pagination-meta.dto';

export class ArticleListDto {
  articles: ArticleDto[];
  meta: PaginationMetaDto;
}
