import { NextRequest, NextResponse } from 'next/server';
import * as fs from 'fs';
import * as path from 'path';

export async function GET(request: NextRequest) {
  try {
    // Path to evaluation results from the backend
    const backendPath = path.join(process.cwd(), '..', 'rfp-auto-responder', 'output', 'evaluation_results.json');
    
    if (!fs.existsSync(backendPath)) {
      return NextResponse.json(
        { error: 'Evaluation results not found. Run: python tests/evaluation.py' },
        { status: 404 }
      );
    }

    const data = JSON.parse(fs.readFileSync(backendPath, 'utf-8'));
    return NextResponse.json(data);
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to load evaluation results', details: String(error) },
      { status: 500 }
    );
  }
}
