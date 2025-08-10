from django.db import models

class Prompt(models.Model):
    """
    Model to store user-submitted prompts for script generation.
    """
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Prompt from {self.created_at.strftime('%Y-%m-%d %H:%M')}"

class Script(models.Model):
    """
    Model to store the generated scripts from the deepscript model.
    """
    prompt = models.ForeignKey(Prompt, on_delete=models.CASCADE, related_name='scripts')
    generated_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Script for '{self.prompt.text[:50]}...'"
