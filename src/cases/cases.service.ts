import { Injectable, InternalServerErrorException } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Case } from './entities/case.entity';
import { Repository } from 'typeorm';
import { CaseDto } from './dto/case.dto';
import * as Docker from 'dockerode';
import { RunCodeDto } from './dto/run-code.dto';
import { PassThrough } from 'stream';
import { CaseListResponseDto } from './dto/case-list.dto';
import { PaginationMetaDto } from './dto/pagination-meta.dto';

@Injectable()
export class CasesService {
  constructor(
    @InjectRepository(Case)
    private caseRepository: Repository<Case>
  ) {}

  async getCases(page: number = 1, limit: number = 10): Promise<CaseListResponseDto> {
    const [cases, total] = await this.caseRepository.findAndCount({
      take: limit,
      skip: (page - 1) * limit,
    });

    const meta: PaginationMetaDto = { total, page, limit };

    return { cases, meta };
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

  async runCode(caseId: number, runCodeDto: RunCodeDto): Promise<any> {
    const { code, lang } = runCodeDto;
    let imageName: string;
    let containerCommand: string[];

    switch (lang) {
      case 'python':
        imageName = 'python:slim';
        containerCommand = ['python3', '-c', code];
        break;

      case 'node':
        imageName = 'node:slim';
        containerCommand = ['node', '-e', code];
        break;

      case 'java':
        imageName = 'openjdk:slim';
        containerCommand = ['java', '-jar', code];
        break;

      default:
        throw new InternalServerErrorException('Unsupported language');
    }

    try {
      const docker: Docker = new Docker()

      const container = await docker.createContainer({
        Image: imageName,
        AttachStdin: false,
        AttachStdout: true,
        AttachStderr: true,
        Tty: false,
        Cmd: containerCommand,
      });

      const outputStream = new PassThrough();
      const logs: string[] = [];
      const stream = await container.attach({
        stream: true,
        stdout: true,
        stderr: true,
      });

      container.modem.demuxStream(stream, outputStream, outputStream);

      outputStream.on('data', (chunk: Buffer) => {
        logs.push(chunk.toString());
      });

      await container.start();

      const waitResult = await container.wait();
      if (waitResult.StatusCode !== 0) {
        throw new InternalServerErrorException('Code execution failed');
      }

      await container.remove();

      return {
        output: logs.join(''),
        exitCode: waitResult.StatusCode,
      };
    } catch (error) {
      throw new InternalServerErrorException('Error running code: ' + error.message);
    }
  }
}
