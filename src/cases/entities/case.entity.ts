import { Entity, PrimaryGeneratedColumn, Column } from 'typeorm';

@Entity()
export class Case {
  @PrimaryGeneratedColumn()
  id: number;

  @Column()
  title: string;

  @Column()
  description: string;

  @Column({ type: 'json', nullable: true })
  testcases: any[];
}
