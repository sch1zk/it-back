import { ApiProperty } from "@nestjs/swagger";

export class CreateCaseDto {
  @ApiProperty()
  title: string;

  @ApiProperty()
  difficulty: 'easy' | 'medium' | 'hard';

  @ApiProperty()
  description: string;

  @ApiProperty()
  initial_code: string;

  @ApiProperty()
  testcases: { params: Record<string, any>; expected: any }[];
}
  