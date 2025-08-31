import React, { useMemo, useState } from "react";
import * as Tabs from "@radix-ui/react-tabs";
import * as Dialog from "@radix-ui/react-dialog";
import JSZip from "jszip";
import { saveAs } from "file-saver";
import axios from "axios";
import { Download, FolderOpen, X } from "lucide-react";
import MarkdownRenderer from "./MarkdownRenderer";

const ListRow = ({ title, sizeKB, onDownload, onPreview }) => (
  <div className="flex items-center justify-between py-3 border-b border-neutral-200">
    <div>
      <div className="text-sm font-medium text-neutral-900">
        {title}
      </div>
      <div className="text-xs text-neutral-500">~{sizeKB} KB</div>
    </div>
    <div className="flex items-center gap-2">
      <button
        onClick={onPreview}
        className="inline-flex items-center gap-2 px-3 py-1.5 text-xs rounded-lg border border-neutral-300 hover:bg-neutral-50"
      >
        Preview
      </button>
      <button
        onClick={onDownload}
        className="inline-flex items-center gap-2 px-3 py-1.5 text-xs rounded-lg bg-blue-600 text-white hover:bg-blue-700"
      >
        <Download className="w-3 h-3" /> Download
      </button>
    </div>
  </div>
);

const ContentCreationDetail = ({ data }) => {
  if (!data) return null;

  const [blogs, setBlogs] = useState(data.blog_posts || []);
  const [emails, setEmails] = useState(data.email_campaigns || []);
  const [activeTab, setActiveTab] = useState("blogs");
  const [previewOpen, setPreviewOpen] = useState(false);
  const [previewItem, setPreviewItem] = useState(null);
  const [regenerating, setRegenerating] = useState(false);

  const API = (process.env.REACT_APP_BACKEND_URL || "") + "/api";

  const downloadText = (name, content) => {
    const fileName = name && name.endsWith('.txt') ? name : `${(name || 'content')}.txt`;
    const blob = new Blob([content || ""], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = fileName;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  };

  const downloadAll = async (type) => {
  const [copied, setCopied] = useState(false);

    const items = type === 'blogs' ? blogs : emails;
    if (!items.length) return;
    const zip = new JSZip();
    items.forEach((it, idx) => {
      const name = (it.name && it.name.endsWith('.txt')) ? it.name : `${(it.name || `${type}-${idx+1}`)}.txt`;
      zip.file(name, it.content || "");
    });
    const city = (data.location?.city || 'city').toLowerCase().replace(/\s+/g, '-');
    const blob = await zip.generateAsync({ type: 'blob' });
    saveAs(blob, `${city}-${type}.zip`);
  };

  const openPreview = (item) => {
    setPreviewItem(item);
    setPreviewOpen(true);
  };

  const regenerate = async () => {
    try {
      setRegenerating(true);
      const zipCode = data.location?.zip_code;
      const { data: assets } = await axios.post(`${API}/zip-analysis/assets/regenerate`, { zip_code: zipCode });
      setBlogs(assets.blog_posts || []);
      setEmails(assets.email_campaigns || []);
    } catch (e) {
      console.error("Regenerate assets error", e);
    } finally {
      setRegenerating(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      {/* Header */}
      <div className="text-center space-y-3">
        <h1 className="text-3xl font-bold text-neutral-900">Content Assets</h1>
        <div className="flex items-center justify-center gap-2 text-neutral-600">
          <FolderOpen className="w-4 h-4" />
          <span className="text-lg">Download blogs and emails for {data.location?.city}, {data.location?.state}</span>
        </div>
        <p className="text-neutral-600 max-w-2xl mx-auto leading-relaxed">
          These assets are generated as plain text (.txt) for maximum compatibility. Use the tabs below to switch between Blogs and Emails.
        </p>
      </div>

      <div className="bg-white rounded-xl border border-neutral-200 shadow-sm">
        <Tabs.Root value={activeTab} onValueChange={setActiveTab}>
          <div className="border-b border-neutral-200 px-4 pt-4">
            <Tabs.List className="flex gap-2">
              <Tabs.Trigger value="blogs" className="px-3 py-2 text-sm font-medium border-b-2 data-[state=active]:border-black data-[state=active]:text-black text-neutral-500">
                Blogs
              </Tabs.Trigger>
              <Tabs.Trigger value="emails" className="px-3 py-2 text-sm font-medium border-b-2 data-[state=active]:border-black data-[state=active]:text-black text-neutral-500">
                Emails
              </Tabs.Trigger>
            </Tabs.List>
          </div>

          <Tabs.Content value="blogs" className="p-4 space-y-3">
            <div className="flex items-center justify-end">
              <button
                onClick={() => downloadAll('blogs')}
                disabled={!blogs.length}
                className="inline-flex items-center gap-2 px-3 py-1.5 text-xs rounded-lg border border-neutral-300 hover:bg-neutral-50"
              >
                <Download className="w-3 h-3" /> Download Blog Posts (.zip)
              </button>
            </div>
            {blogs.length === 0 ? (
              <div className="flex items-center justify-between">
                <div className="text-sm text-neutral-500">No blog posts available yet.</div>
                <button
                  onClick={regenerate}
                  disabled={regenerating}
                  className="inline-flex items-center gap-2 px-3 py-1.5 text-xs rounded-lg border border-neutral-300 hover:bg-neutral-50"
                >
                  {regenerating ? 'Generating…' : 'Generate Assets'}
                </button>
              </div>
            ) : (
              <div className="divide-y divide-neutral-200">
                {blogs.map((b, idx) => (
                  <ListRow
                    key={idx}
                    title={b.title || b.name}
                    sizeKB={b.size_kb || Math.max(1, Math.floor((b.content || '').length / 1024))}
                    onDownload={() => downloadText(b.name || `blog-${idx+1}.txt`, b.content)}
                    onPreview={() => openPreview(b)}
                  />
                ))}
              </div>
            )}
          </Tabs.Content>

          <Tabs.Content value="emails" className="p-4 space-y-3">
            <div className="flex items-center justify-end">
              <button
                onClick={() => downloadAll('emails')}
                disabled={!emails.length}
                className="inline-flex items-center gap-2 px-3 py-1.5 text-xs rounded-lg border border-neutral-300 hover:bg-neutral-50"
              >
                <Download className="w-3 h-3" /> Download Emails (.zip)
              </button>
            </div>
            {emails.length === 0 ? (
              <div className="flex items-center justify-between">
                <div className="text-sm text-neutral-500">No emails available yet.</div>
                <button
                  onClick={regenerate}
                  disabled={regenerating}
                  className="inline-flex items-center gap-2 px-3 py-1.5 text-xs rounded-lg border border-neutral-300 hover:bg-neutral-50"
                >
                  {regenerating ? 'Generating…' : 'Generate Assets'}
                </button>
              </div>
            ) : (
              <div className="divide-y divide-neutral-200">
                {emails.map((e, idx) => (
                  <ListRow
                    key={idx}
                    title={e.title || e.name}
                    sizeKB={e.size_kb || Math.max(1, Math.floor((e.content || '').length / 1024))}
                    onDownload={() => downloadText(e.name || `email-${idx+1}.txt`, e.content)}
                    onPreview={() => openPreview(e)}
                  />
                ))}
              </div>
            )}
          </Tabs.Content>
        </Tabs.Root>
      </div>

      {/* Preview Drawer */}
      <Dialog.Root open={previewOpen} onOpenChange={setPreviewOpen}>
        <Dialog.Portal>
          <Dialog.Overlay className="fixed inset-0 bg-black/30" />
          <Dialog.Content className="fixed right-0 top-0 h-full w-full sm:w-[520px] bg-white shadow-xl border-l border-neutral-200 flex flex-col">
            <div className="flex items-center justify-between p-4 border-b border-neutral-200">
              <Dialog.Title className="text-base font-semibold text-neutral-900 truncate pr-4">
                {previewItem?.title || previewItem?.name}
              </Dialog.Title>
              <Dialog.Close className="inline-flex items-center justify-center w-8 h-8 rounded-lg hover:bg-neutral-100">
                <X className="w-4 h-4" />
              </Dialog.Close>
            </div>
            <div className="p-4 flex-1 overflow-auto">
              <div className="prose max-w-none">
                <MarkdownRenderer content={previewItem?.content || ''} className="prose-sm" />
              </div>
            </div>
            <div className="p-4 border-t border-neutral-200 flex items-center gap-2">
              <button
                onClick={() => previewItem && downloadText(previewItem.name, previewItem.content)}
                className="inline-flex items-center gap-2 px-3 py-2 text-sm rounded-lg bg-blue-600 text-white hover:bg-blue-700"
              >
                <Download className="w-4 h-4" /> Download .txt
              </button>
              <CopyButton text={previewItem?.content || ''} />
            </div>
          </Dialog.Content>
        </Dialog.Portal>
      </Dialog.Root>
    </div>
  );
};


function CopyButton({ text }) {
  const [copied, setCopied] = useState(false);
  return (
    <button
      onClick={() => {
        navigator.clipboard.writeText(text || '');
        setCopied(true);
        setTimeout(() => setCopied(false), 1500);
      }}
      className={`inline-flex items-center gap-2 px-3 py-2 text-sm rounded-lg border ${copied ? 'bg-green-50 border-green-300 text-green-800' : 'border-neutral-300 hover:bg-neutral-50'}`}
      aria-live="polite"
    >
      {copied ? 'Content Copied!' : 'Copy Text'}
    </button>
  );
}

export default ContentCreationDetail;