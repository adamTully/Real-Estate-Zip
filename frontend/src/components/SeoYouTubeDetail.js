import React, { useMemo } from "react";
import { Search, ListTree } from "lucide-react";
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

const SeoYouTubeDetail = ({ data }) => {
  if (!data) return null;

  const content = data.analysis_content || data.optimization_summary || "No analysis available";
  const headings = useMemo(() => extractHeadings(content), [content]);

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      {/* Header */}
      <div className="text-center space-y-3">
        <h1 className="text-3xl font-bold text-neutral-900">SEO & YouTube Trends Analysis</h1>
        <div className="flex items-center justify-center gap-2 text-neutral-600">
          <Search className="w-4 h-4" />
          <span className="text-lg">{data.location?.city}, {data.location?.state} Market Analysis</span>
        </div>
        <p className="text-neutral-600 max-w-2xl mx-auto leading-relaxed">
          Keyword trends, long-tail questions, video title ideas, and implementation tips styled for quick scanning.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
        {/* Main content */}
        <div className="lg:col-span-2 space-y-6">
          <ContentBlock>
            <MarkdownRenderer content={content} className="prose-lg" />
          </ContentBlock>
        </div>

        {/* Outline (sticky) */}
        <div className="lg:col-span-1">
          <div className="lg:sticky lg:top-24 space-y-4">
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
          </div>
        </div>
      </div>
    </div>
  );
};

export default SeoYouTubeDetail;