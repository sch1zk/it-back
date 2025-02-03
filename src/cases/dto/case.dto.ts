import { ApiProperty } from "@nestjs/swagger";

export class CaseDto {
  @ApiProperty()
  id: number;

  @ApiProperty()
  title: string;

  @ApiProperty()
  description: string;
}