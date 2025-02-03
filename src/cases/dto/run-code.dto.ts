import { ApiProperty } from '@nestjs/swagger';
import { IsString } from 'class-validator';

export class RunCodeDto {
  @ApiProperty()
  @IsString()
  code: string;

  @ApiProperty()
  @IsString()
  lang: string;

  @ApiProperty()
  @IsString()
  args?: string[]
}
