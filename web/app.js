(() => {
    const $ = (selector) => document.querySelector(selector);
    const el = {
        fileInput: $('#fileInput'),
        shuffleButton: $('#shuffleButton'),
        exportButton: $('#exportButton'),
        copyButton: $('#copyButton'),
        dropZone: $('#dropZone'),
        fileName: $('#fileName'),
        recordCount: $('#recordCount'),
        summaryBody: $('#summaryBody'),
        previewText: $('#previewText'),
        previewCount: $('#previewCount'),
        helpButton: $('#helpButton'),
        helpDialog: $('#helpDialog'),
        helpContent: $('#helpContent'),
        closeHelpButton: $('#closeHelpButton'),
    };
    const state = {description: '', records: [], shuffled: []};
    const csvPickerOptions = {
        multiple: false,
        excludeAcceptAllOption: true,
        types: [{description: 'CSV(逗号分隔)', accept: {'text/csv': ['.csv']}}],
    };

    function decode(buffer) {
        const utf8 = new TextDecoder('utf-8').decode(buffer);
        if (!utf8.includes('\uFFFD')) return utf8.replace(/^\uFEFF/, '');
        try {
            return new TextDecoder('gbk').decode(buffer).replace(/^\uFEFF/, '');
        } catch {
            return utf8;
        }
    }

    function parseCsv(text) {
        const rows = [];
        let row = [];
        let value = '';
        let quoted = false;
        const quote = String.fromCharCode(34);
        for (let index = 0; index < text.length; index += 1) {
            const char = text[index];
            if (char === quote) {
                if (quoted && text[index + 1] === quote) {
                    value += quote;
                    index += 1;
                } else quoted = !quoted;
            } else if (char === ',' && !quoted) {
                row.push(value);
                value = '';
            } else if ((char === '\n' || char === '\r') && !quoted) {
                if (char === '\r' && text[index + 1] === '\n') index += 1;
                row.push(value);
                rows.push(row);
                row = [];
                value = '';
            } else value += char;
        }
        if (value || row.length) {
            row.push(value);
            rows.push(row);
        }
        return rows.filter((item) => item.some((cell) => cell.trim()));
    }

    function randomize(records) {
        const result = [...records];
        for (let index = result.length - 1; index > 0; index -= 1) {
            const target = Math.floor(Math.random() * (index + 1));
            [result[index], result[target]] = [result[target], result[index]];
        }
        return result;
    }

    function line(record, index) {
        return `${index + 1}.${record.notes ? `${record.name}-${record.notes}` : record.name}`;
    }

    function renderSummary() {
        const counts = new Map();
        state.records.forEach((record) => {
            if (record.notes) counts.set(record.notes, (counts.get(record.notes) || 0) + 1);
        });
        const items = [...counts].sort((first, second) => second[1] - first[1] || first[0].localeCompare(second[0], 'zh-CN'));
        el.summaryBody.replaceChildren();
        if (!items.length) {
            el.summaryBody.innerHTML = '<tr><td colspan=2>无非空内容</td></tr>';
            return;
        }
        items.forEach(([note, count]) => {
            const row = document.createElement('tr');
            const noteCell = document.createElement('td');
            const countCell = document.createElement('td');
            noteCell.textContent = note;
            countCell.textContent = count;
            row.append(noteCell, countCell);
            el.summaryBody.append(row);
        });
    }

    function renderPreview() {
        const lines = state.description ? [state.description, ''] : [];
        state.shuffled.slice(0, 20).forEach((record, index) => lines.push(line(record, index)));
        if (state.shuffled.length > 20) lines.push('', `... 仅预览展示前 20 行，其余 ${state.shuffled.length - 20} 行将在导出时完整写入 ...`);
        el.previewText.textContent = lines.join('\n') || '导入 CSV 文件后将在这里显示排序结果。';
        el.previewCount.textContent = `${state.shuffled.length} 条`;
    }

    async function importFile(file) {
        if (!file) return;
        if (!file.name.toLowerCase().endsWith('.csv')) return;
        try {
            const rows = parseCsv(decode(await file.arrayBuffer()));
            const records = rows.slice(1).reduce((result, row) => {
                const name = (row[0] || '').trim();
                if (name) result.push({name, notes: (row[1] || '').trim()});
                return result;
            }, []);
            if (!rows.length) throw new Error('CSV 文件未检测到有效内容。');
            state.description = (rows[0][0] || '').trim();
            state.records = records;
            state.shuffled = randomize(records);
            el.fileName.textContent = file.name;
            el.recordCount.textContent = records.length;
            renderSummary();
            renderPreview();
            el.shuffleButton.disabled = !records.length;
            el.exportButton.disabled = !records.length;
            el.copyButton.disabled = !records.length;
        } catch (error) {
            console.error('读取 CSV 文件失败：', error);
        } finally {
            el.fileInput.value = '';
        }
    }

    function refresh() {
        state.shuffled = randomize(state.records);
        renderPreview();
    }

    async function showHelp() {
        el.helpContent.textContent = '正在加载使用说明…';
        el.helpDialog.showModal();
        try {
            const response = await fetch('instruction.txt', {cache: 'no-store'});
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            el.helpContent.textContent = await response.text();
        } catch (error) {
            console.error('加载使用说明失败：', error);
            el.helpContent.textContent = '使用说明加载失败，请稍后重试。';
        }
    }

    function outputText() {
        const lines = state.description ? [state.description, ''] : [];
        state.shuffled.forEach((record, index) => lines.push(line(record, index)));
        return `${lines.join('\n')}\n`;
    }

    function exportFile() {
        const link = document.createElement('a');
        link.href = URL.createObjectURL(new Blob([outputText()], {type: 'text/plain;charset=utf-8'}));
        link.download = `接龙排序结果-${new Date().toISOString().slice(0, 10)}.txt`;
        link.click();
        URL.revokeObjectURL(link.href);
    }

    async function copyToClipboard() {
        try {
            if (navigator.clipboard && window.isSecureContext) {
                await navigator.clipboard.writeText(outputText());
            } else {
                const textArea = document.createElement('textarea');
                textArea.value = outputText();
                textArea.style.position = 'fixed';
                textArea.style.opacity = '0';
                document.body.append(textArea);
                textArea.select();
                const copied = document.execCommand('copy');
                textArea.remove();
                if (!copied) throw new Error('浏览器未授予剪贴板权限');
            }
            el.copyButton.textContent = '已复制';
        } catch (error) {
            console.error('复制到剪贴板失败：', error);
            el.copyButton.textContent = '复制失败';
        }
        window.setTimeout(() => {
            el.copyButton.textContent = '复制到剪贴板';
        }, 1600);
    }

    async function choose() {
        if (!window.isSecureContext || !window.showOpenFilePicker) {
            el.fileInput.click();
            return;
        }
        try {
            const [fileHandle] = await window.showOpenFilePicker(csvPickerOptions);
            await importFile(await fileHandle.getFile());
        } catch (error) {
            if (error.name !== 'AbortError') console.error('打开 CSV 文件失败：', error);
        }
    }

    window.addEventListener('dragover', (event) => event.preventDefault());
    window.addEventListener('drop', (event) => event.preventDefault());
    el.dropZone.addEventListener('click', choose);
    el.fileInput.addEventListener('change', (event) => importFile(event.target.files[0]));
    el.shuffleButton.addEventListener('click', refresh);
    el.exportButton.addEventListener('click', exportFile);
    el.copyButton.addEventListener('click', copyToClipboard);
    el.dropZone.addEventListener('keydown', (event) => {
        if (event.key === 'Enter' || event.key === ' ') {
            event.preventDefault();
            choose();
        }
    });
    ['dragenter', 'dragover'].forEach((name) => el.dropZone.addEventListener(name, (event) => {
        event.preventDefault();
        el.dropZone.classList.add('is-dragover');
    }));
    ['dragleave', 'drop'].forEach((name) => el.dropZone.addEventListener(name, (event) => {
        event.preventDefault();
        el.dropZone.classList.remove('is-dragover');
    }));
    el.dropZone.addEventListener('drop', (event) => importFile(event.dataTransfer.files[0]));
    el.helpButton.addEventListener('click', showHelp);
    el.closeHelpButton.addEventListener('click', () => el.helpDialog.close());
})();
