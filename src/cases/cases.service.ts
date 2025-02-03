import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Case } from './entities/case.entity';
import { Repository } from 'typeorm';
import { CaseDto } from './dto/case.dto';

@Injectable()
export class CasesService {
  constructor(
    @InjectRepository(Case)
    private caseRepository: Repository<Case>,
  ) {}

  async getAllCases(page: number = 1, limit: number = 10): Promise<CaseDto[]> {
    const [cases, total] = await this.caseRepository.findAndCount({
      take: limit,
      skip: (page - 1) * limit,
    });

    return cases.map(caseItem => ({
      id: caseItem.id,
      title: caseItem.title,
      description: caseItem.description,
    }));
  }

  async getCaseById(id: number): Promise<CaseDto> {
    const caseItem = await this.caseRepository.findOne({ where: { id } });
    if (!caseItem) {
      throw new Error('Case not found');
    }

    return {
      id: caseItem.id,
      title: caseItem.title,
      description: caseItem.description,
    };
  }
}
