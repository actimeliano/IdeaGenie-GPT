document.addEventListener('DOMContentLoaded', () => {
    const initialTitle = document.getElementById('initial-title');
    const initialIdea = document.getElementById('initial-idea');
    const generateBtn = document.getElementById('generate-btn');
    const pauseBtn = document.getElementById('pause-btn');
    const titlesOutput = document.getElementById('titles-output');
    const ideasOutput = document.getElementById('ideas-output');

    let isGenerating = false;
    let feedback = [];

    generateBtn.addEventListener('click', startGeneration);
    pauseBtn.addEventListener('click', pauseGeneration);

    function startGeneration() {
        isGenerating = true;
        generateBtn.style.display = 'none';
        pauseBtn.style.display = 'inline-block';
        generateContent();
    }

    function pauseGeneration() {
        isGenerating = false;
        generateBtn.style.display = 'inline-block';
        pauseBtn.style.display = 'none';
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
                        feedback: feedback
                    }),
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const data = await response.json();
                displayContent(data);
            } catch (error) {
                console.error('Error generating content:', error);
                titlesOutput.innerHTML = '<p>Error: Unable to generate content</p>';
                ideasOutput.innerHTML = '<p>Error: Unable to generate content</p>';
                pauseGeneration();
            }

            await new Promise(resolve => setTimeout(resolve, 5000)); // Wait for 5 seconds before next generation
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
        
        const contentSpan = document.createElement('span');
        contentSpan.className = 'item-content';
        contentSpan.textContent = item.content;
        
        const feedbackDiv = document.createElement('div');
        feedbackDiv.className = 'feedback-buttons';
        
        const likeBtn = document.createElement('button');
        likeBtn.innerHTML = '✓';
        likeBtn.className = 'feedback-btn';
        likeBtn.onclick = () => addFeedback(item.content, type, true);
        
        const dislikeBtn = document.createElement('button');
        dislikeBtn.innerHTML = '✗';
        dislikeBtn.className = 'feedback-btn';
        dislikeBtn.onclick = () => addFeedback(item.content, type, false);
        
        feedbackDiv.appendChild(likeBtn);
        feedbackDiv.appendChild(dislikeBtn);
        
        div.appendChild(contentSpan);
        div.appendChild(feedbackDiv);
        
        return div;
    }

    function addFeedback(content, type, isPositive) {
        feedback.push({
            content: content,
            type: type,
            feedback: isPositive ? 'positive' : 'negative'
        });
    }
});
