import statistics
import random

def generate_sample_data(size=100):
    """Generate sample data for analysis."""
    return [random.randint(1, 100) for _ in range(size)]

def calculate_statistics(data):
    """Calculate basic statistics for a dataset."""
    if not data:
        return None
    
    return {
        'count': len(data),
        'mean': statistics.mean(data),
        'median': statistics.median(data),
        'mode': statistics.mode(data) if len(set(data)) < len(data) else None,
        'std_dev': statistics.stdev(data) if len(data) > 1 else 0,
        'min': min(data),
        'max': max(data),
        'range': max(data) - min(data)
    }

def filter_outliers(data, threshold=2):
    """Remove outliers from data based on standard deviation."""
    if len(data) < 2:
        return data
    
    mean = statistics.mean(data)
    std_dev = statistics.stdev(data)
    
    return [x for x in data if abs(x - mean) <= threshold * std_dev]

def categorize_data(data, categories=3):
    """Categorize data into low, medium, high groups."""
    if not data:
        return {}
    
    min_val = min(data)
    max_val = max(data)
    range_size = (max_val - min_val) / categories
    
    categorized = {'low': [], 'medium': [], 'high': []}
    
    for value in data:
        if value <= min_val + range_size:
            categorized['low'].append(value)
        elif value <= min_val + 2 * range_size:
            categorized['medium'].append(value)
        else:
            categorized['high'].append(value)
    
    return categorized

if __name__ == "__main__":
    # Demo analysis
    print("Data Analysis Demo")
    
    # Generate sample data
    data = generate_sample_data(50)
    print(f"Generated {len(data)} data points")
    
    # Calculate statistics
    stats = calculate_statistics(data)
    print("Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Filter outliers
    clean_data = filter_outliers(data)
    print(f"After removing outliers: {len(clean_data)} data points")
    
    # Categorize
    categories = categorize_data(clean_data)
    print("Categorized data:")
    for category, values in categories.items():
        print(f"  {category}: {len(values)} values")
