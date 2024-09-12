document.addEventListener('DOMContentLoaded', () => {
    const initialTitle = document.getElementById('initial-title');
    const initialIdea = document.getElementById('initial-idea');
    const modelSelect = document.getElementById('model-select');
    const customModel = document.getElementById('custom-model');
    const generateBtn = document.getElementById('generate-btn');
    const pauseBtn = document.getElementById('pause-btn');
    const newSessionBtn = document.getElementById('new-session-btn');
    const exportBtn = document.getElementById('export-btn');
    const titlesOutput = document.getElementById('titles-output');
    const ideasOutput = document.getElementById('ideas-output');
    const positiveFeedbackList = document.getElementById('positive-feedback');
    const negativeFeedbackList = document.getElementById('negative-feedback');

    let isGenerating = false;
    let feedback = [];
    let currentSessionId = null;

    generateBtn.addEventListener('click', startGeneration);
    pauseBtn.addEventListener('click', pauseGeneration);
    newSessionBtn.addEventListener('click', startNewSession);
    exportBtn.addEventListener('click', exportSession);

    function startGeneration() {
        isGenerating = true;
        generateBtn.style.display = 'none';
        pauseBtn.style.display = 'inline-block';
        exportBtn.style.display = 'inline-block';
        generateContent();
    }

    function pauseGeneration() {
        isGenerating = false;
        generateBtn.style.display = 'inline-block';
        pauseBtn.style.display = 'none';
    }

    function startNewSession() {
        currentSessionId = null;
        feedback = [];
        titlesOutput.innerHTML = '';
        ideasOutput.innerHTML = '';
        initialTitle.value = '';
        initialIdea.value = '';
        pauseGeneration();
        exportBtn.style.display = 'none';
        clearMindMap();
        updateFeedbackDisplay();
    }

    function exportSession() {
        if (currentSessionId) {
            window.location.href = `/export/${currentSessionId}`;
        } else {
            alert('No session to export. Please generate some ideas first.');
        }
    }

    async function generateContent() {
        while (isGenerating) {
            try {
                const response = await fetch('/generate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        initial_title: initialTitle.value,
                        initial_idea: initialIdea.value,
                        feedback: feedback,
                        session_id: currentSessionId,
                        model: customModel.value || modelSelect.value
                    }),
                });

                if (response.status === 401) {
                    window.location.href = '/login';
                    return;
                }

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const data = await response.json();
                currentSessionId = data.session_id;
                displayContent(data);
                updateMindMap();
                updateFeedbackDisplay();
                
                // Clear feedback after each generation
                feedback = [];
            } catch (error) {
                console.error('Error generating content:', error);
                titlesOutput.innerHTML = '<p>Error: Unable to generate content</p>';
                ideasOutput.innerHTML = '<p>Error: Unable to generate content</p>';
                pauseGeneration();
            }

            await new Promise(resolve => setTimeout(resolve, 5000));
        }
    }

    function displayContent(data) {
        titlesOutput.innerHTML = '';
        ideasOutput.innerHTML = '';

        if (data && data.titles && Array.isArray(data.titles)) {
            data.titles.forEach(title => {
                titlesOutput.appendChild(createItemElement(title, 'title'));
            });
        } else {
            console.error('Invalid or missing titles data:', data);
            titlesOutput.innerHTML = '<p>Error: Unable to display titles</p>';
        }

        if (data && data.ideas && Array.isArray(data.ideas)) {
            data.ideas.forEach(idea => {
                ideasOutput.appendChild(createItemElement(idea, 'idea'));
            });
        } else {
            console.error('Invalid or missing ideas data:', data);
            ideasOutput.innerHTML = '<p>Error: Unable to display ideas</p>';
        }
    }

    function createItemElement(item, type) {
        const div = document.createElement('div');
        div.className = `item ${item.category}`;
        div.dataset.id = item.id;
        
        const contentSpan = document.createElement('span');
        contentSpan.className = 'item-content';
        contentSpan.textContent = item.content;
        
        const feedbackDiv = document.createElement('div');
        feedbackDiv.className = 'feedback-buttons';
        
        const likeBtn = document.createElement('button');
        likeBtn.innerHTML = '✓';
        likeBtn.className = 'feedback-btn';
        likeBtn.onclick = (event) => addFeedback(event, item.content, type, true);
        
        const dislikeBtn = document.createElement('button');
        dislikeBtn.innerHTML = '✗';
        dislikeBtn.className = 'feedback-btn';
        dislikeBtn.onclick = (event) => addFeedback(event, item.content, type, false);
        
        feedbackDiv.appendChild(likeBtn);
        feedbackDiv.appendChild(dislikeBtn);
        
        div.appendChild(contentSpan);
        div.appendChild(feedbackDiv);
        
        div.addEventListener('click', () => selectIdea(item.id));
        
        return div;
    }

    function addFeedback(event, content, type, isPositive) {
        feedback.push({
            content: content,
            type: type,
            feedback: isPositive ? 'positive' : 'negative'
        });
        
        // Add visual feedback
        const feedbackBtn = event.target;
        feedbackBtn.classList.add('selected');
        setTimeout(() => feedbackBtn.classList.remove('selected'), 500);
        
        console.log('Feedback added:', feedback[feedback.length - 1]);
        updateFeedbackDisplay();
    }

    function updateFeedbackDisplay() {
        positiveFeedbackList.innerHTML = '';
        negativeFeedbackList.innerHTML = '';

        feedback.forEach(item => {
            const li = document.createElement('li');
            li.textContent = `${item.type.charAt(0).toUpperCase() + item.type.slice(1)}: ${item.content}`;
            
            if (item.feedback === 'positive') {
                positiveFeedbackList.appendChild(li);
            } else {
                negativeFeedbackList.appendChild(li);
            }
        });
    }

    let selectedIdeas = [];

    function selectIdea(id) {
        if (selectedIdeas.includes(id)) {
            selectedIdeas = selectedIdeas.filter(ideaId => ideaId !== id);
        } else {
            selectedIdeas.push(id);
        }

        if (selectedIdeas.length === 2) {
            addRelationship(selectedIdeas[0], selectedIdeas[1]);
            selectedIdeas = [];
        }

        updateSelectedIdeasVisual();
    }

    function updateSelectedIdeasVisual() {
        document.querySelectorAll('.item').forEach(item => {
            if (selectedIdeas.includes(parseInt(item.dataset.id))) {
                item.classList.add('selected');
            } else {
                item.classList.remove('selected');
            }
        });
    }

    async function addRelationship(idea1Id, idea2Id) {
        try {
            const response = await fetch('/add_relationship', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    idea1_id: idea1Id,
                    idea2_id: idea2Id,
                    session_id: currentSessionId
                }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            updateMindMap();
        } catch (error) {
            console.error('Error adding relationship:', error);
        }
    }

    // Mind Map Visualization
    let svg, simulation, link, node;

    function initMindMap() {
        const width = 600;
        const height = 400;

        svg = d3.select("#mind-map")
            .append("svg")
            .attr("width", width)
            .attr("height", height);

        simulation = d3.forceSimulation()
            .force("link", d3.forceLink().id(d => d.id))
            .force("charge", d3.forceManyBody())
            .force("center", d3.forceCenter(width / 2, height / 2));
    }

    async function updateMindMap() {
        if (!currentSessionId) return;

        try {
            const response = await fetch(`/mind_map/${currentSessionId}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            renderMindMap(data);
        } catch (error) {
            console.error('Error updating mind map:', error);
        }
    }

    function renderMindMap(data) {
        if (!svg) initMindMap();

        link = svg.selectAll(".link")
            .data(data.links)
            .join("line")
            .attr("class", "link");

        node = svg.selectAll(".node")
            .data(data.nodes)
            .join("g")
            .attr("class", "node")
            .call(d3.drag()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended));

        node.append("circle")
            .attr("r", 5)
            .attr("fill", d => d.type === 'title' ? 'red' : 'blue');

        node.append("text")
            .attr("dx", 12)
            .attr("dy", ".35em")
            .text(d => d.name);

        simulation
            .nodes(data.nodes)
            .on("tick", ticked);

        simulation.force("link")
            .links(data.links);

        simulation.alpha(1).restart();
    }

    function ticked() {
        link
            .attr("x1", d => d.source.x)
            .attr("y1", d => d.source.y)
            .attr("x2", d => d.target.x)
            .attr("y2", d => d.target.y);

        node
            .attr("transform", d => `translate(${d.x},${d.y})`);
    }

    function dragstarted(event) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        event.subject.fx = event.subject.x;
        event.subject.fy = event.subject.y;
    }

    function dragged(event) {
        event.subject.fx = event.x;
        event.subject.fy = event.y;
    }

    function dragended(event) {
        if (!event.active) simulation.alphaTarget(0);
        event.subject.fx = null;
        event.subject.fy = null;
    }

    function clearMindMap() {
        if (svg) {
            svg.selectAll("*").remove();
        }
    }

    initMindMap();
});
