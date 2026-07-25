document.addEventListener('DOMContentLoaded', () => {
    // Navigation Tabs Setup
    const navItems = document.querySelectorAll('.nav-item');
    const tabPages = document.querySelectorAll('.tab-page');
    const tabTitle = document.getElementById('tab-title');

    const titles = {
        'documents-tab': 'Document Management & ML Classification',
        'search-tab': 'Semantic Search & RAG Question Answering',
        'analysis-tab': 'Document Summarization & Comparison Engine',
        'analytics-tab': 'System Analytics & Knowledge Base Metrics'
    };

    navItems.forEach(item => {
        item.addEventListener('click', () => {
            const targetTab = item.getAttribute('data-tab');
            navItems.forEach(i => i.classList.remove('active'));
            tabPages.forEach(p => p.classList.remove('active'));

            item.classList.add('active');
            document.getElementById(targetTab).classList.add('active');
            tabTitle.textContent = titles[targetTab] || 'Dashboard';

            if (targetTab === 'documents-tab') loadDocuments();
            if (targetTab === 'analysis-tab') populateDocSelectors();
            if (targetTab === 'analytics-tab') loadAnalytics();
        });
    });

    // Initial Data Load
    loadDocuments();

    // Refresh Button
    document.getElementById('refresh-btn').addEventListener('click', () => {
        loadDocuments();
        populateDocSelectors();
        loadAnalytics();
    });

    // --- UPLOAD HANDLER ---
    const dropZone = document.getElementById('drop-zone');
    const pdfFileInput = document.getElementById('pdf-file-input');
    const uploadProgress = document.getElementById('upload-progress');

    dropZone.addEventListener('click', () => pdfFileInput.click());

    pdfFileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            uploadFile(e.target.files[0]);
        }
    });

    function uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);

        uploadProgress.classList.remove('hidden');

        fetch('/api/v1/documents/upload', {
            method: 'POST',
            body: formData
        })
        .then(res => res.json())
        .then(data => {
            uploadProgress.classList.add('hidden');
            alert(data.message || 'File uploaded successfully!');
            loadDocuments();
        })
        .catch(err => {
            uploadProgress.classList.add('hidden');
            alert('Upload failed: ' + err.message);
        });
    }

    // --- LOAD DOCUMENTS TABLE ---
    function loadDocuments() {
        fetch('/api/v1/documents')
            .then(res => res.json())
            .then(data => {
                const tbody = document.getElementById('documents-table-body');
                tbody.innerHTML = '';

                if (!data.documents || data.documents.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="6" class="text-center">No documents uploaded yet.</td></tr>';
                    return;
                }

                data.documents.forEach(doc => {
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td><strong>${doc.file_name}</strong></td>
                        <td><span class="badge badge-info">${doc.category || 'Unclassified'}</span></td>
                        <td>${doc.total_pages}</td>
                        <td>${doc.total_chunks}</td>
                        <td><span class="badge ${doc.processing_status === 'PROCESSED' ? 'badge-success' : 'badge-warning'}">${doc.processing_status}</span></td>
                        <td>
                            <button class="btn btn-danger" onclick="deleteDoc('${doc.doc_id}')">Delete</button>
                        </td>
                    `;
                    tbody.appendChild(tr);
                });
            });
    }

    window.deleteDoc = function(docId) {
        if (confirm('Are you sure you want to delete this document?')) {
            fetch(`/api/v1/documents/${docId}`, { method: 'DELETE' })
                .then(res => res.json())
                .then(data => {
                    alert(data.message);
                    loadDocuments();
                });
        }
    };

    // --- ML CLASSIFIER PLAYGROUND ---
    document.getElementById('btn-run-classify').addEventListener('click', () => {
        const text = document.getElementById('classify-input-text').value;
        if (!text.trim()) return alert('Please enter sample text.');

        fetch('/api/v1/analysis/classify-text', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text })
        })
        .then(res => res.json())
        .then(data => {
            const badge = document.getElementById('classification-result-badge');
            badge.textContent = `Domain: ${data.category} (${(data.confidence * 100).toFixed(1)}%)`;
            badge.className = 'badge badge-success';
            badge.classList.remove('hidden');
        });
    });

    // --- CHAT & RAG HANDLER ---
    const chatInput = document.getElementById('chat-input');
    const sendChatBtn = document.getElementById('send-chat-btn');
    const chatMessages = document.getElementById('chat-messages');

    sendChatBtn.addEventListener('click', sendQuestion);
    chatInput.addEventListener('keypress', (e) => { if (e.key === 'Enter') sendQuestion(); });

    function sendQuestion() {
        const query = chatInput.value.trim();
        if (!query) return;

        // Render user message
        appendMessage('user', query);
        chatInput.value = '';

        const mode = document.getElementById('search-mode-select').value;

        fetch('/api/v1/search/qa', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                query: query,
                search_mode: mode,
                session_id: 'web_session_1'
            })
        })
        .then(res => res.json())
        .then(data => {
            appendMessage('assistant', data.answer, data.citations);
        })
        .catch(err => {
            appendMessage('assistant', 'Error fetching answer: ' + err.message);
        });
    }

    function appendMessage(sender, text, citations = []) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${sender === 'user' ? 'user-msg' : 'assistant-msg'}`;

        let citationsHTML = '';
        if (citations && citations.length > 0) {
            citationsHTML = '<div>' + citations.map(c => `<span class="citation-chip">📄 ${c.document} (Page ${c.page})</span>`).join('') + '</div>';
        }

        msgDiv.innerHTML = `
            <div class="msg-avatar">${sender === 'user' ? '👤' : '🤖'}</div>
            <div class="msg-content">
                ${text.replace(/\n/g, '<br>')}
                ${citationsHTML}
            </div>
        `;
        chatMessages.appendChild(msgDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // --- POPULATE DOC SELECTORS ---
    function populateDocSelectors() {
        fetch('/api/v1/documents')
            .then(res => res.json())
            .then(data => {
                const sumSelect = document.getElementById('summarize-doc-select');
                const compSelect = document.getElementById('compare-doc-select');

                sumSelect.innerHTML = '<option value="">-- Choose Document --</option>';
                compSelect.innerHTML = '';

                (data.documents || []).forEach(doc => {
                    sumSelect.innerHTML += `<option value="${doc.doc_id}">${doc.file_name}</option>`;
                    compSelect.innerHTML += `<option value="${doc.doc_id}">${doc.file_name}</option>`;
                });
            });
    }

    // --- SUMMARIZATION HANDLER ---
    document.getElementById('btn-generate-summary').addEventListener('click', () => {
        const docId = document.getElementById('summarize-doc-select').value;
        if (!docId) return alert('Select a document first.');

        const resultBox = document.getElementById('summary-result');
        resultBox.innerHTML = 'Generating multi-tier summary...';
        resultBox.classList.remove('hidden');

        fetch('/api/v1/analysis/summarize', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ doc_id: docId })
        })
        .then(res => res.json())
        .then(data => {
            const s = data.summary;
            resultBox.innerHTML = `
                <h4>Executive Summary</h4><p>${s.executive_summary || s.summary || ''}</p>
                <h4 style="margin-top:12px;">Technical Summary</h4><p>${s.technical_summary || ''}</p>
                <h4 style="margin-top:12px;">Bullet Points</h4>
                <ul>${(s.bullet_points || []).map(p => `<li>${p}</li>`).join('')}</ul>
                <h4 style="margin-top:12px;">Key Takeaways</h4>
                <ul>${(s.key_takeaways || []).map(k => `<li>${k}</li>`).join('')}</ul>
            `;
        });
    });

    // --- COMPARISON HANDLER ---
    document.getElementById('btn-generate-comparison').addEventListener('click', () => {
        const compSelect = document.getElementById('compare-doc-select');
        const selectedDocIds = Array.from(compSelect.selectedOptions).map(o => o.value);

        if (selectedDocIds.length < 2) return alert('Please select at least 2 documents.');

        const resultBox = document.getElementById('comparison-result');
        resultBox.innerHTML = 'Running comparative analysis across documents...';
        resultBox.classList.remove('hidden');

        fetch('/api/v1/analysis/compare', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ doc_ids: selectedDocIds })
        })
        .then(res => res.json())
        .then(data => {
            resultBox.innerHTML = `<div>${(data.comparison_matrix || '').replace(/\n/g, '<br>')}</div>`;
        });
    });

    // --- ANALYTICS HANDLER ---
    function loadAnalytics() {
        fetch('/api/v1/analytics/dashboard')
            .then(res => res.json())
            .then(data => {
                document.getElementById('stat-total-docs').textContent = data.total_documents;
                document.getElementById('stat-total-chunks').textContent = data.total_processed_chunks;
                document.getElementById('stat-total-queries').textContent = data.total_questions_answered;

                // Category distribution
                const catContainer = document.getElementById('category-dist-container');
                catContainer.innerHTML = '';
                for (const [cat, count] of Object.entries(data.category_distribution || {})) {
                    catContainer.innerHTML += `<div style="display:flex; justify-content:space-between; margin-bottom:8px;"><span>${cat}</span><strong>${count} docs</strong></div>`;
                }

                // Recent queries
                const qContainer = document.getElementById('recent-queries-container');
                qContainer.innerHTML = (data.recent_queries || []).map(q => `<div style="padding:6px 0; border-bottom:1px solid var(--border-color); font-size:13px;"><strong>Query:</strong> ${q.query} <span style="color:var(--text-muted);">(${q.search_type})</span></div>`).join('');
            });
    }
});
