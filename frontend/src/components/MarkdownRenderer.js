import React, { useEffect, useState, Suspense } from "react";

function slugify(children) {
  try {
    const text = React.Children.toArray(children).map((c) => {
      if (typeof c === "string") return c;
      if (typeof c?.props?.children === "string") return c.props.children;
      return "";
    }).join(" ");
    return text.toLowerCase().replace(/[^a-z0-9\s-]/g, "").trim().replace(/\s+/g, "-");
  } catch {
    return undefined;
  }
}

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
        if (mounted) setFailed(true);
      }
    }
    load();
    return () => { mounted = false; };
  }, []);

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
          h1: ({ node, children, ...props }) => (
            <h1
              id={slugify(children)}
              className="scroll-mt-20 text-[clamp(28px,4.5vw,40px)] font-extrabold tracking-tight text-neutral-900 mt-6 mb-4"
              {...props}
            >
              {children}
            </h1>
          ),
          h2: ({ node, children, ...props }) => (
            <h2
              id={slugify(children)}
              className="scroll-mt-20 text-[clamp(22px,3.5vw,32px)] font-bold text-neutral-900 mt-10 mb-3 pt-4 border-t border-neutral-200"
              {...props}
            >
              {children}
            </h2>
          ),
          h3: ({ node, children, ...props }) => (
            <h3
              id={slugify(children)}
              className="scroll-mt-20 text-[clamp(18px,3vw,24px)] font-semibold text-neutral-900 mt-8 mb-2"
              {...props}
            >
              {children}
            </h3>
          ),
          p: ({ node, ...props }) => (
            <p className="mb-3 leading-relaxed text-neutral-800" {...props} />
          ),
          ul: ({ node, ...props }) => (
            <ul className="list-disc pl-5 space-y-1 mb-3 text-neutral-800" {...props} />
          ),
          ol: ({ node, ...props }) => (
            <ol className="list-decimal pl-5 space-y-1 mb-3 text-neutral-800" {...props} />
          ),
          li: ({ node, ordered, ...props }) => (
            <li className="ml-1" {...props} />
          ),
          strong: ({ node, ...props }) => (
            <strong className="font-semibold text-neutral-900" {...props} />
          ),
          em: ({ node, ...props }) => (
            <em className="italic" {...props} />
          ),
          a: ({ node, ...props }) => (
            <a className="text-blue-600 hover:underline" target="_blank" rel="noreferrer" {...props} />
          ),
          code: ({ inline, className: cn, children, ...props }) => (
            <code className={`bg-neutral-100 px-1.5 py-0.5 rounded ${cn || ""}`} {...props}>
              {children}
            </code>
          ),
          table: ({ node, ...props }) => (
            <div className="overflow-auto mb-4">
              <table className="min-w-full text-sm border border-neutral-200" {...props} />
            </div>
          ),
          th: ({ node, ...props }) => (
            <th className="bg-neutral-50 border border-neutral-200 px-3 py-2 text-left font-semibold" {...props} />
          ),
          td: ({ node, ...props }) => (
            <td className="border border-neutral-200 px-3 py-2" {...props} />
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