import React from 'react';
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Tooltip,
} from 'recharts';

export default function RiskRadarChart({ scores }) {
  const data = [
    { subject: 'Financial (25%)', score: scores?.financial || 0 },
    { subject: 'Cybersecurity (25%)', score: scores?.cybersecurity || 0 },
    { subject: 'Compliance (20%)', score: scores?.compliance || 0 },
    { subject: 'Operational (20%)', score: scores?.operational || 0 },
    { subject: 'Reputation (10%)', score: scores?.reputation || 0 },
  ];

  return (
    <div className="w-full h-72">
      <ResponsiveContainer width="100%" height="100%">
        <RadarChart cx="50%" cy="50%" outerRadius="80%" data={data}>
          <PolarGrid stroke="#e2e8f0" />
          <PolarAngleAxis dataKey="subject" tick={{ fill: '#475569', fontSize: 12 }} />
          <PolarRadiusAxis angle={30} domain={[0, 100]} stroke="#cbd5e1" />
          <Radar
            name="Risk Score (0-100)"
            dataKey="score"
            stroke="#0284c7"
            fill="#38bdf8"
            fillOpacity={0.45}
          />
          <Tooltip />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
}

