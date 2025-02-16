import { ApiProperty } from "@nestjs/swagger";

export class UpdateProfileDto {
    @ApiProperty({ required: false })
    bio?: string;
  
    @ApiProperty({ required: false })
    dateOfBirth?: Date;
  }