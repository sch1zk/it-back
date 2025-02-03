import { CaseDto } from './case.dto';
import { PaginationMetaDto } from './pagination-meta.dto';

export class CaseListResponseDto {
  cases: CaseDto[];
  meta: PaginationMetaDto;
}
