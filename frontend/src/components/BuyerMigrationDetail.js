import React, { useMemo } from "react";
import { MapPin, TrendingUp, Target, Lightbulb, Quote, AlertCircle, ListTree } from "lucide-react";
import MarkdownRenderer from "./MarkdownRenderer";

const ContentBlock = ({ children, className = "" }) => (
  <div className={`bg-white rounded-xl p-6 border border-neutral-200 shadow-sm ${className}`}>
    {children}
  </div>
);

function extractHeadings(md) {
  try {
    const lines = (md || "").split("\n");
    const headings = [];
    lines.forEach((line) => {
      const m = line.match(/^(#{1,3})\s+(.+)/);
      if (m) {
        const level = m[1].length;
        const text = m[2].trim();
        const id = text.toLowerCase().replace(/[^a-z0-9\s-]/g, "").replace(/\s+/g, "-");
        headings.push({ level, text, id });
      }
    });
    return headings;
  } catch {
    return [];
  }
}

const BuyerMigrationDetailView = ({ data }) => {
  if (!data) return null;

  const content = data.analysis_content || data.market_overview || "No analysis available";
  const headings = useMemo(() => extractHeadings(content), [content]);

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      {/* Header */}
      <div className="text-center space-y-3">
        <h1 className="text-3xl font-bold text-neutral-900">Buyer Migration Intelligence</h1>
        <div className="flex items-center justify-center gap-2 text-neutral-600">
          <MapPin className="w-4 h-4" />
          <span className="text-lg">{data.location?.city}, {data.location?.state} Market Analysis</span>
        </div>
        <p className="text-neutral-600 max-w-2xl mx-auto leading-relaxed">
          Narrative report with clearly structured sections and skimmable typography.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
        {/* Main content */}
        <div className="lg:col-span-2 space-y-6">
          <ContentBlock>
            <MarkdownRenderer content={content} className="prose-lg" />
          </ContentBlock>
        </div>

        {/* Outline */}
        <div className="lg:col-span-1">
          <ContentBlock>
            <div className="flex items-center gap-2 mb-3">
              <ListTree className="w-4 h-4 text-neutral-600" />
              <h3 className="text-sm font-semibold text-neutral-900">Outline</h3>
            </div>
            {headings.length ? (
              <ul className="space-y-1 text-sm">
                {headings.map((h, idx) => (
                  <li key={idx} className={`text-neutral-700 ${h.level === 1 ? 'font-semibold' : h.level === 2 ? 'pl-3' : 'pl-5'}`}>
                    <a href={`#${h.id}`} className="hover:text-blue-600">
                      {h.text}
                    </a>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-neutral-500 text-sm">Headings will appear here.</p>
            )}
          </ContentBlock>

          {/* Quick Tips */}
          <ContentBlock>
            <h3 className="text-sm font-semibold text-neutral-900 mb-2">How to use this report</h3>
            <ul className="list-disc pl-5 space-y-1 text-sm text-neutral-700">
              <li>Scan the Market Overview for a quick summary</li>
              <li>Use "Where Buyers Are Coming From" to target relocation ads</li>
              <li>Turn Hooks and Video Titles into short-form content</li>
              <li>Apply Quick Actions this week to capture demand</li>
            </ul>
          </ContentBlock>
        </div>
      </div>

      {/* Error Handling */}
      {data.error && (
        <ContentBlock className="bg-red-50 border-red-200">
          <div className="flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-600 mt-1 flex-shrink-0" />
            <div>
              <h3 className="text-lg font-semibold text-red-900 mb-2">Analysis Temporarily Unavailable</h3>
              <p className="text-red-800 leading-relaxed">We're experiencing temporary issues generating real-time analysis. Please try again in a few moments.</p>
              <p className="text-xs text-red-600 mt-2">Error: {data.error}</p>
            </div>
          </div>
        </ContentBlock>
      )}
    </div>
  );
};

export default BuyerMigrationDetailView;