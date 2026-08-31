import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

export async function GET() {
  try {
    const filePath = path.join(process.cwd(), '..', 'rfp-auto-responder', 'output', 'retry_flows.json');

    // If file doesn't exist, return empty array
    if (!fs.existsSync(filePath)) {
      return NextResponse.json({
        flows: [],
        message: 'No retry flows recorded yet. Run evaluation to populate.'
      });
    }

    const data = JSON.parse(fs.readFileSync(filePath, 'utf-8'));

    return NextResponse.json({ flows: data.flows || [] });
  } catch (error) {
    console.error('Error reading retry flows:', error);
    return NextResponse.json({ flows: [] }, { status: 200 });
  }
}
