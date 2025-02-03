import { Body, Controller, Get, Param, Post, Query } from '@nestjs/common';
import { CasesService } from './cases.service';
import { ApiOperation, ApiResponse } from '@nestjs/swagger';
import { CaseDto } from './dto/case.dto';
import { RunCodeDto } from './dto/run-code.dto';

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

  @Post(':id/run')
  @ApiOperation({ summary: 'Run user code in a Docker container' })
  @ApiResponse({ status: 200, description: 'Code executed successfully' })
  async runCode(
    @Param('id') id: number,
    @Body() runCodeDto: RunCodeDto,
  ): Promise<any> {
    return this.casesService.runCode(id, runCodeDto);
  }
}
