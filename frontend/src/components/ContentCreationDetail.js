import React, { useMemo, useState } from "react";
import * as Tabs from "@radix-ui/react-tabs";
import * as Dialog from "@radix-ui/react-dialog";
import JSZip from "jszip";
import { saveAs } from "file-saver";
import { Download, Mail, FileText, FolderOpen, X } from "lucide-react";

const ListRow = ({ title, sizeKB, onDownload, onPreview }) => (
  <div className="flex items-center justify-between py-3 border-b border-neutral-200">
    <button onClick={onPreview} className="text-left">
      <div className="text-sm font-medium text-neutral-900 hover:text-blue-600">{title}</div>
      <div className="text-xs text-neutral-500">~{sizeKB} KB</div>
    </button>
    <button
      onClick={onDownload}
      className="inline-flex items-center gap-2 px-3 py-1.5 text-xs rounded-lg bg-blue-600 text-white hover:bg-blue-700"
    >
      <Download className="w-3 h-3" /> Download
    </button>
  </div>
);

const ContentCreationDetail = ({ data }) => {
  if (!data) return null;

  const blogs = useMemo(() => data.blog_posts || [], [data]);
  const emails = useMemo(() => data.email_campaigns || [], [data]);

  const [activeTab, setActiveTab] = useState("blogs");
  const [previewOpen, setPreviewOpen] = useState(false);
  const [previewItem, setPreviewItem] = useState(null);

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
          <div className="border-b border-neutral-200 px-4 pt-4 flex items-center justify-between">
            <Tabs.List className="flex gap-2">
              <Tabs.Trigger value="blogs" className="px-3 py-2 text-sm font-medium border-b-2 data-[state=active]:border-black data-[state=active]:text-black text-neutral-500">
                Blogs
              </Tabs.Trigger>
              <Tabs.Trigger value="emails" className="px-3 py-2 text-sm font-medium border-b-2 data-[state=active]:border-black data-[state=active]:text-black text-neutral-500">
                Emails
              </Tabs.Trigger>
            </Tabs.List>

            {/* Group download buttons */}
            <div />
          </div>

          <Tabs.Content value="blogs" className="p-4">
            {blogs.length === 0 ? (
              <div className="text-sm text-neutral-500">No blog posts available yet.</div>
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

          <Tabs.Content value="emails" className="p-4">
            {emails.length === 0 ? (
              <div className="text-sm text-neutral-500">No emails available yet.</div>
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
              <pre className="whitespace-pre-wrap text-sm leading-relaxed text-neutral-800">{previewItem?.content}</pre>
            </div>
            <div className="p-4 border-t border-neutral-200">
              <button
                onClick={() => previewItem && downloadText(previewItem.name, previewItem.content)}
                className="inline-flex items-center gap-2 px-3 py-2 text-sm rounded-lg bg-blue-600 text-white hover:bg-blue-700"
              >
                <Download className="w-4 h-4" /> Download .txt
              </button>
            </div>
          </Dialog.Content>
        </Dialog.Portal>
      </Dialog.Root>
    </div>
  );
};

export default ContentCreationDetail;