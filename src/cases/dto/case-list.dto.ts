import { CaseDto } from './case.dto';
import { PaginationMetaDto } from 'dto/pagination-meta.dto';

export class CaseListDto {
  cases: CaseDto[];
  meta: PaginationMetaDto;
}
