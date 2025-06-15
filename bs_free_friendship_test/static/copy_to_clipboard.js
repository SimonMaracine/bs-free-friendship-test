function copy_link_to_clipboard() {
    const quiz_link = document.getElementById("quiz_link")

    navigator.clipboard.writeText(quiz_link.value)
}
