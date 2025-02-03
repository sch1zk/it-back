import { Controller, Get, Param, Query } from '@nestjs/common';
import { CasesService } from './cases.service';
import { ApiOperation, ApiResponse } from '@nestjs/swagger';
import { CaseDto } from './dto/case.dto';

@Controller('cases')
export class CasesController {
  constructor(private readonly casesService: CasesService) {}

  @Get()
  @ApiOperation({ summary: 'Get all cases with pagination' })
  @ApiResponse({ status: 200, description: 'List of cases', type: [CaseDto] })
  async getAllCases(
    @Query('page') page: number = 1,
    @Query('limit') limit: number = 10,
  ): Promise<CaseDto[]> {
    return this.casesService.getAllCases(page, limit);
  }

  @Get(':id')
  @ApiOperation({ summary: 'Get case details by id' })
  @ApiResponse({ status: 200, description: 'Case details', type: CaseDto })
  async getCaseById(@Param('id') id: number): Promise<CaseDto> {
    return this.casesService.getCaseById(id);
  }
}
