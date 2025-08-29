import React, { useEffect, useState, Suspense } from "react";

// Lightweight Markdown renderer with graceful fallback
// - Prefers react-markdown + remark-gfm if available
// - Falls back to simple pre-wrapped text if the deps are not installed

const MarkdownRenderer = ({ content = "", className = "" }) => {
  const [ReactMarkdown, setReactMarkdown] = useState(null);
  const [gfm, setGfm] = useState(null);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    let mounted = true;
    async function load() {
      try {
        const [{ default: RM }, { default: gfmPlugin }] = await Promise.all([
          import("react-markdown"),
          import("remark-gfm"),
        ]);
        if (mounted) {
          setReactMarkdown(() => RM);
          setGfm(() => gfmPlugin);
        }
      } catch (e) {
        // Dependencies not installed yet; fallback to simple rendering
        if (mounted) setFailed(true);
      }
    }
    load();
    return () => {
      mounted = false;
    };
  }, []);

  // Normalize common non-string shapes (e.g., { text: "..." })
  const normalized = typeof content === "string"
    ? content
    : content?.text || content?.message || JSON.stringify(content || "", null, 2);

  if (failed || !ReactMarkdown) {
    return (
      <div className={`leading-relaxed text-neutral-800 whitespace-pre-wrap ${className}`}>
        {normalized}
      </div>
    );
  }

  const RM = ReactMarkdown;

  return (
    <Suspense fallback={<div className={`text-sm text-neutral-500 ${className}`}>Rendering…</div>}>
      <RM
        remarkPlugins={gfm ? [gfm] : []}
        components={{
          h1: ({ node, ...props }) => (
            <h1 className="text-3xl font-bold text-neutral-900 mt-6 mb-4" {...props} />
          ),
          h2: ({ node, ...props }) => (
            <h2 className="text-2xl font-semibold text-neutral-900 mt-6 mb-3" {...props} />
          ),
          h3: ({ node, ...props }) => (
            <h3 className="text-xl font-semibold text-neutral-900 mt-5 mb-2" {...props} />
          ),
          p: ({ node, ...props }) => (
            <p className="mb-3 leading-relaxed text-neutral-800" {...props} />
          ),
          li: ({ node, ordered, ...props }) => (
            <li className="ml-4 mb-1" {...props} />
          ),
          strong: ({ node, ...props }) => (
            <strong className="font-semibold text-neutral-900" {...props} />
          ),
          em: ({ node, ...props }) => (
            <em className="italic" {...props} />
          ),
          a: ({ node, ...props }) => (
            <a className="text-blue-600 hover:underline" {...props} />
          ),
          code: ({ inline, className: cn, children, ...props }) => (
            <code className={`bg-neutral-100 px-1.5 py-0.5 rounded ${cn || ""}`} {...props}>
              {children}
            </code>
          ),
        }}
        className={`prose max-w-none ${className}`}
      >
        {normalized}
      </RM>
    </Suspense>
  );
};

export default MarkdownRenderer;