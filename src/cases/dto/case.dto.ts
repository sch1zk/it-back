import { ApiProperty } from "@nestjs/swagger";
import { IsArray, IsOptional } from "class-validator";

export class CaseDto {
  @ApiProperty()
  id: number;

  @ApiProperty()
  title: string;

  @ApiProperty()
  description: string;

  @ApiProperty({
    description: 'Testcase array. Every testcase is object with input data end expected value. Ex: { "input": { "nums": [2,7,11,15], "target": 9 }, "expected": [0,1] }',
    example: [
      { input: { nums: [2,7,11,15], target: 9 }, expected: [0,1] },
      { input: { nums: [3,2,4], target: 6 }, expected: [1,2] }
    ]
  })
  @IsOptional()
  @IsArray()
  testcases?: any[];
}