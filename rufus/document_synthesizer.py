class DocumentSynthesizer:
    def __init__(self):
        pass

    def synthesize(self, scraped_data , prompt):
        """
        Synthesize the json into a plain text
        """
        output = ""
        for page in scraped_data:
            for element in page['page_text']:
                if element['type'] in ['h1', 'h2']:  # If it's a heading, make it uppercase
                    output += f"{element['text'].upper()}\n\n"
                else:  # For other, make it normal case
                    output += f"{element['text']}\n\n"
        output += "\n"
        return output
