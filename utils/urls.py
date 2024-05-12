from urllib.parse import urlparse

def is_valid_url(url):
    try:
        result = urlparse(url)
        # Check if the URL has both a valid scheme and a network location (netloc)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

if __name__=="__main__":
  # Examples of using the function
  test_urls = [
      "http://example.com",
      "https://www.google.com",
      "ftp://example.com/file.txt",
      "example.com",  # This will return False because it lacks a scheme
      "not a url",    # This will return False
      "https://",     # This will return False because it lacks a netloc
  ]

  for url in test_urls:
      print(f"Is '{url}' a valid URL? {is_valid_url(url)}")
