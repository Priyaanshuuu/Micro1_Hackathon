import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

export async function GET() {
  try {
    const filePath = path.join(process.cwd(), '..', 'rfp-auto-responder', 'output', 'baseline_comparison.json');

    if (!fs.existsSync(filePath)) {
      return NextResponse.json({
        error: 'Baseline comparison data not found',
        message: 'Run: python baseline_comparison.py'
      }, { status: 404 });
    }

    const data = JSON.parse(fs.readFileSync(filePath, 'utf-8'));

    return NextResponse.json(data);
  } catch (error) {
    console.error('Error reading baseline comparison:', error);
    return NextResponse.json({ error: 'Failed to load baseline comparison' }, { status: 500 });
  }
}
