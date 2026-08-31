import { NextRequest, NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

function parseCSV(csvContent: string): Record<string, string>[] {
  const lines = csvContent.trim().split('\n');
  if (lines.length === 0) return [];

  const headers = lines[0].split(',').map(h => h.trim());
  const records: Record<string, string>[] = [];

  for (let i = 1; i < lines.length; i++) {
    if (!lines[i].trim()) continue;
    const values = lines[i].split(',').map(v => v.trim());
    const record: Record<string, string> = {};
    
    headers.forEach((header, index) => {
      record[header] = values[index] || '';
    });
    
    records.push(record);
  }

  return records;
}

export async function GET(request: NextRequest) {
  try {
    const csvPath = path.join(
      process.cwd(),
      '..',
      'rfp-auto-responder',
      'output',
      'human_review_queue.csv'
    );

    if (!fs.existsSync(csvPath)) {
      return NextResponse.json(
        {
          error: 'No escalated questions found. Run the evaluation pipeline to generate data.',
          escalated_questions: [],
          total: 0
        },
        { status: 200 }
      );
    }

    const fileContent = fs.readFileSync(csvPath, 'utf-8');
    const records = parseCSV(fileContent);

    return NextResponse.json({
      escalated_questions: records,
      total: records.length
    });
  } catch (error) {
    console.error('Error reading human review queue:', error);
    return NextResponse.json(
      {
        error: 'Failed to read human review queue',
        escalated_questions: [],
        total: 0
      },
      { status: 200 }
    );
  }
}
