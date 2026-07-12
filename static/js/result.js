document.addEventListener("DOMContentLoaded", () => {
    const downloadButton = document.getElementById("download-image-button");
    const resultCard = document.getElementById("capture-area");
    const statusMessage = document.getElementById("download-status");

    if (!downloadButton || !resultCard) {
        return;
    }

    downloadButton.addEventListener("click", async () => {
        const originalText = downloadButton.textContent;

        downloadButton.disabled = true;
        downloadButton.textContent = "画像を作成中…";

        if (statusMessage) {
            statusMessage.textContent = "";
        }

        try {
            /*
             * ボタン類は画像に含めないため、
             * data-html2canvas-ignore 属性を付けています。
             */
            const canvas = await html2canvas(resultCard, {
                backgroundColor: "#151722",
                scale: 2,
                useCORS: true,
                allowTaint: false,
                logging: false,
                imageTimeout: 15000
            });

            const imageUrl = canvas.toDataURL("image/png");

            const nickname =
                resultCard.dataset.nickname || "genshin-profile";

            const uid =
                resultCard.dataset.uid || "unknown";

            const safeNickname = nickname.replace(
                /[\\/:*?"<>|]/g,
                "_"
            );

            const link = document.createElement("a");

            link.href = imageUrl;
            link.download =
                `${safeNickname}_${uid}_profile-rank.png`;

            document.body.appendChild(link);
            link.click();
            link.remove();

            if (statusMessage) {
                statusMessage.textContent =
                    "結果画像を保存しました。";
            }
        } catch (error) {
            console.error("画像生成エラー:", error);

            if (statusMessage) {
                statusMessage.textContent =
                    "画像を作成できませんでした。ブラウザを更新して、もう一度お試しください。";
            }
        } finally {
            downloadButton.disabled = false;
            downloadButton.textContent = originalText;
        }
    });
});