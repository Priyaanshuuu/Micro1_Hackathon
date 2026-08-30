import { NextRequest, NextResponse } from 'next/server';
import * as fs from 'fs';
import * as path from 'path';

export async function GET(request: NextRequest) {
  try {
    // Path to responses CSV from the backend
    const backendPath = path.join(process.cwd(), '..', 'rfp-auto-responder', 'output', 'responses.csv');
    
    if (!fs.existsSync(backendPath)) {
      return NextResponse.json(
        { error: 'Responses not found. Run: python -m src.main' },
        { status: 404 }
      );
    }

    const csvContent = fs.readFileSync(backendPath, 'utf-8');
    const lines = csvContent.trim().split('\n');
    const headers = lines[0].split(',');
    
    const responses = lines.slice(1).map(line => {
      const values = line.split(',');
      const obj: any = {};
      headers.forEach((header, index) => {
        obj[header.trim()] = values[index]?.trim() || '';
      });
      return obj;
    });

    // Calculate summary stats
    const approved = responses.filter(r => r.status === 'approved').length;
    const escalated = responses.filter(r => r.status === 'escalated').length;
    const totalRetries = responses.reduce((sum, r) => sum + parseInt(r.retries || 0), 0);

    return NextResponse.json({
      total: responses.length,
      approved,
      escalated,
      approved_percentage: responses.length > 0 ? (approved / responses.length * 100).toFixed(1) : 0,
      escalation_percentage: responses.length > 0 ? (escalated / responses.length * 100).toFixed(1) : 0,
      avg_retries: responses.length > 0 ? (totalRetries / responses.length).toFixed(2) : 0,
      total_retries: totalRetries,
      responses
    });
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to load responses', details: String(error) },
      { status: 500 }
    );
  }
}
