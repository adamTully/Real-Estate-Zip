@@
-import React, { useMemo, useState } from "react";
+import React, { useMemo, useState } from "react";
 import * as Tabs from "@radix-ui/react-tabs";
 import * as Dialog from "@radix-ui/react-dialog";
 import JSZip from "jszip";
 import { saveAs } from "file-saver";
+import axios from "axios";
 import { Download, Mail, FileText, FolderOpen, X } from "lucide-react";
@@
-  const blogs = useMemo(() => data.blog_posts || [], [data]);
-  const emails = useMemo(() => data.email_campaigns || [], [data]);
+  const [blogs, setBlogs] = useState(data.blog_posts || []);
+  const [emails, setEmails] = useState(data.email_campaigns || []);
+  const [regenerating, setRegenerating] = useState(false);
@@
   const openPreview = (item) => {
     setPreviewItem(item);
     setPreviewOpen(true);
   };
+
+  const API = process.env.REACT_APP_BACKEND_URL + "/api";
+  const regenerate = async () => {
+    try {
+      setRegenerating(true);
+      const zipCode = data.location?.zip_code;
+      const { data: assets } = await axios.post(`${API}/zip-analysis/assets/regenerate`, { zip_code: zipCode });
+      setBlogs(assets.blog_posts || []);
+      setEmails(assets.email_campaigns || []);
+    } catch (e) {
+      // no-op: parent toasts handle errors in other flows
+      console.error("Regenerate assets error", e);
+    } finally {
+      setRegenerating(false);
+    }
+  };
@@
-          <Tabs.Content value="blogs" className="p-4 space-y-3">
+          <Tabs.Content value="blogs" className="p-4 space-y-3">
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
-              <div className="text-sm text-neutral-500">No blog posts available yet.</div>
+              <div className="flex items-center justify-between">
+                <div className="text-sm text-neutral-500">No blog posts available yet.</div>
+                <button
+                  onClick={regenerate}
+                  disabled={regenerating}
+                  className="inline-flex items-center gap-2 px-3 py-1.5 text-xs rounded-lg border border-neutral-300 hover:bg-neutral-50"
+                >
+                  {regenerating ? 'Generating…' : 'Generate Assets'}
+                </button>
+              </div>
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
@@
-          <Tabs.Content value="emails" className="p-4 space-y-3">
+          <Tabs.Content value="emails" className="p-4 space-y-3">
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
-              <div className="text-sm text-neutral-500">No emails available yet.</div>
+              <div className="flex items-center justify-between">
+                <div className="text-sm text-neutral-500">No emails available yet.</div>
+                <button
+                  onClick={regenerate}
+                  disabled={regenerating}
+                  className="inline-flex items-center gap-2 px-3 py-1.5 text-xs rounded-lg border border-neutral-300 hover:bg-neutral-50"
+                >
+                  {regenerating ? 'Generating…' : 'Generate Assets'}
+                </button>
+              </div>
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
@@
             <div className="p-4 border-t border-neutral-200">
               <button
                 onClick={() => previewItem && downloadText(previewItem.name, previewItem.content)}
                 className="inline-flex items-center gap-2 px-3 py-2 text-sm rounded-lg bg-blue-600 text-white hover:bg-blue-700 mr-2"
               >
                 <Download className="w-4 h-4" /> Download .txt
               </button>
+              <button
+                onClick={() => navigator.clipboard.writeText(previewItem?.content || '')}
+                className="inline-flex items-center gap-2 px-3 py-2 text-sm rounded-lg border border-neutral-300 hover:bg-neutral-50"
+              >
+                Copy Text
+              </button>
             </div>
@@
 export default ContentCreationDetail;