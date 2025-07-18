import { ApiProperty } from "@nestjs/swagger";

export class CaseDto {
  @ApiProperty()
  id: number;

  @ApiProperty()
  title: string;

  @ApiProperty()
  difficulty: 'easy' | 'medium' | 'hard';

  @ApiProperty()
  description: string;

  @ApiProperty()
  initial_code: string;

  @ApiProperty()
  testcases: { params: Record<string, any>; expected: any; }[];
}