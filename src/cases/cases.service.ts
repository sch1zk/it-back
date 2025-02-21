import { HttpException, HttpStatus, Injectable, InternalServerErrorException, NotFoundException } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Case } from './entities/case.entity';
import { Repository } from 'typeorm';
import { CaseDto } from './dto/case.dto';
import { CaseListDto } from './dto/case-list.dto';
import { PaginationMetaDto } from 'dto/pagination-meta.dto';
import { CreateCaseDto } from './dto/create-case.dto';
import { UpdateCaseDto } from './dto/update-case-dto';
import { RunCodeDto } from './dto/run-code.dto';

interface TestResult {
  params: Record<string, any>;
  expected: any;
  output: any;
  passed: boolean;
}

@Injectable()
export class CasesService {
  constructor(
    @InjectRepository(Case)
    private caseRepository: Repository<Case>
  ) {}

  async getCases(page: number = 1, limit: number = 10): Promise<CaseListDto> {
    const [cases, total] = await this.caseRepository.findAndCount({
      take: limit,
      skip: (page - 1) * limit,
      order: { created_at: 'DESC' },
    });

    const meta: PaginationMetaDto = { total, page, limit };

    return { cases, meta };
  }

  async getCaseById(id: number, hiddenMode: boolean = false): Promise<CaseDto> {
    const caseItem = await this.caseRepository.findOne({ where: { id } });
    if (!caseItem) {
      throw new NotFoundException('Case not found');
    }

    if (hiddenMode) {
      const limitedTestcases = caseItem.testcases.slice(0, 3);

      limitedTestcases.forEach(testcase => {
        delete testcase.expected;
      });

      return { ...caseItem, testcases: limitedTestcases };
    }

    return caseItem;
  }

  async createCase(createCaseDto: CreateCaseDto): Promise<CaseDto> {
    const newCase = this.caseRepository.create(createCaseDto);
    return await this.caseRepository.save(newCase);
  }

  async updateCase(id: number, updateCaseDto: UpdateCaseDto): Promise<CaseDto> {
    const caseItem = await this.caseRepository.preload({
      id,
      ...updateCaseDto,
    });

    if (!caseItem) {
      throw new NotFoundException('Case not found');
    }

    return await this.caseRepository.save(caseItem);
  }

  async deleteCase(id: number): Promise<void> {
    const result = await this.caseRepository.delete(id);
    if (result.affected === 0) {
      throw new NotFoundException('Case not found');
    }
  }

  async runCode(caseId: number, { code, lang }: RunCodeDto) {
    try {
      const caseItem = await this.getCaseById(caseId);
      const results: TestResult[] = [];

      for (const { params, expected } of caseItem.testcases) {
        const res = await fetch('http://localhost:6060/run', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ code, lang }),
        });
  
        if (!res.ok) {
          throw new HttpException('Failed to execute code', HttpStatus.INTERNAL_SERVER_ERROR);
        }
  
        const { output } = await res.json();
        const passed = output.trim() === expected;
        results.push({ params, expected, output, passed });
      }

      return { caseId, results };
    } catch (error) {
      throw new HttpException('Execution error', HttpStatus.INTERNAL_SERVER_ERROR);
    }
  }
}
