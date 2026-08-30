import { NextRequest, NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';
import csv from 'csv-parse/sync';

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
        { status: 200 } // Return 200 with empty data instead of 404
      );
    }

    const fileContent = fs.readFileSync(csvPath, 'utf-8');
    const records = csv.parse(fileContent, {
      columns: true,
      skip_empty_lines: true
    });

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
