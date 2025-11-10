"""
Create Default Avatar Image
Run this script once to generate a default avatar image for users
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_default_avatar():
    """Create a default avatar image with user icon"""
    
    # Create directory if it doesn't exist
    os.makedirs('static/images', exist_ok=True)
    
    # Image settings
    size = 400
    background_color = (102, 126, 234)  # #667eea
    
    # Create image
    img = Image.new('RGB', (size, size), background_color)
    draw = ImageDraw.Draw(img)
    
    # Draw user icon (simplified)
    center_x, center_y = size // 2, size // 2
    
    # Head circle
    head_radius = 80
    draw.ellipse(
        [center_x - head_radius, center_y - 120 - head_radius,
         center_x + head_radius, center_y - 120 + head_radius],
        fill='white'
    )
    
    # Body (semicircle)
    body_width = 180
    body_height = 120
    draw.ellipse(
        [center_x - body_width, center_y + 20,
         center_x + body_width, center_y + 20 + body_height * 2],
        fill='white'
    )
    
    # Save image
    img.save('static/images/default-avatar.png', 'PNG', quality=95)
    print("✅ Default avatar created: static/images/default-avatar.png")
    
    # Also create a smaller version for navbar
    img_small = img.resize((200, 200), Image.Resampling.LANCZOS)
    img_small.save('static/images/default-avatar-small.png', 'PNG', quality=95)
    print("✅ Small avatar created: static/images/default-avatar-small.png")

def create_placeholder_avatars():
    """Create multiple colored placeholder avatars"""
    
    colors = [
        ('#667eea', 'purple'),
        ('#f59e0b', 'orange'),
        ('#10b981', 'green'),
        ('#3b82f6', 'blue'),
        ('#ef4444', 'red'),
        ('#8b5cf6', 'violet')
    ]
    
    size = 400
    
    for color_hex, color_name in colors:
        # Convert hex to RGB
        r = int(color_hex[1:3], 16)
        g = int(color_hex[3:5], 16)
        b = int(color_hex[5:7], 16)
        
        # Create image
        img = Image.new('RGB', (size, size), (r, g, b))
        draw = ImageDraw.Draw(img)
        
        center_x, center_y = size // 2, size // 2
        
        # Draw user icon
        head_radius = 80
        draw.ellipse(
            [center_x - head_radius, center_y - 120 - head_radius,
             center_x + head_radius, center_y - 120 + head_radius],
            fill='white'
        )
        
        body_width = 180
        body_height = 120
        draw.ellipse(
            [center_x - body_width, center_y + 20,
             center_x + body_width, center_y + 20 + body_height * 2],
            fill='white'
        )
        
        # Save
        img.save(f'static/images/avatar-{color_name}.png', 'PNG', quality=95)
        print(f"✅ Created avatar: static/images/avatar-{color_name}.png")

def create_avatar_with_initial(initial='U', background_color='#667eea'):
    """Create avatar with user initial"""
    
    size = 400
    
    # Convert hex to RGB
    r = int(background_color[1:3], 16)
    g = int(background_color[3:5], 16)
    b = int(background_color[5:7], 16)
    
    # Create image
    img = Image.new('RGB', (size, size), (r, g, b))
    draw = ImageDraw.Draw(img)
    
    # Try to use a font, fallback to default if not available
    try:
        font = ImageFont.truetype("arial.ttf", 200)
    except:
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 200)
        except:
            font = ImageFont.load_default()
    
    # Draw initial
    text = initial.upper()
    
    # Get text bounding box
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Center text
    x = (size - text_width) // 2
    y = (size - text_height) // 2 - 20
    
    draw.text((x, y), text, fill='white', font=font)
    
    # Save
    img.save('static/images/avatar-initial.png', 'PNG', quality=95)
    print("✅ Created avatar with initial: static/images/avatar-initial.png")

if __name__ == '__main__':
    print("Creating default avatar images...")
    print("-" * 50)
    
    # Create main default avatar
    create_default_avatar()
    
    # Create colored variants
    print("\nCreating colored variants...")
    create_placeholder_avatars()
    
    # Create avatar with initial
    print("\nCreating avatar with initial...")
    create_avatar_with_initial('U', '#667eea')
    
    print("\n" + "=" * 50)
    print("✅ All avatar images created successfully!")
    print("=" * 50)