from django.core.management.base import BaseCommand
from dash.models import Tags  # <-- replace 'your_app' with the actual app name

class Command(BaseCommand):
    help = 'Bulk insert/update political & regional tags for BIGSTORY Network'

    def handle(self, *args, **kwargs):
        tags_data = [
            # Political Leaders
            {
                'title': 'Donald Trump',
                'description': 'News and updates on former US President Donald Trump.',
                'meta_title': 'Donald Trump News – BIGSTORY Network',
                'meta_description': 'Coverage of Donald Trump’s political activities, policies, and global impact.',
                'meta_keywords': 'Donald Trump, US Politics, BIGSTORY America'
            },
            {
                'title': 'PM Modi',
                'description': 'News and updates on Prime Minister Narendra Modi.',
                'meta_title': 'PM Modi News & Updates – BIGSTORY Network',
                'meta_description': 'Coverage of Narendra Modi’s policies, speeches, and governance.',
                'meta_keywords': 'PM Modi, Narendra Modi, Indian Prime Minister, BIGSTORY Politics'
            },
            {
                'title': 'Rahul Gandhi',
                'description': 'Coverage of Rahul Gandhi’s political activities and views.',
                'meta_title': 'Rahul Gandhi News – BIGSTORY Network',
                'meta_description': 'Updates on Rahul Gandhi’s speeches, campaigns, and political work.',
                'meta_keywords': 'Rahul Gandhi, Indian National Congress, BIGSTORY Politics'
            },
            {
                'title': 'Sonia Gandhi',
                'description': 'News and updates on Sonia Gandhi’s political role.',
                'meta_title': 'Sonia Gandhi News – BIGSTORY Network',
                'meta_description': 'Coverage of Sonia Gandhi’s leadership, party role, and statements.',
                'meta_keywords': 'Sonia Gandhi, Indian Politics, BIGSTORY Politics'
            },
            {
                'title': 'Amit Shah',
                'description': 'Coverage of Amit Shah’s political strategies and leadership.',
                'meta_title': 'Amit Shah News – BIGSTORY Network',
                'meta_description': 'News on Amit Shah’s role, policies, and political activities.',
                'meta_keywords': 'Amit Shah, BJP, Indian Politics, BIGSTORY Politics'
            },
            {
                'title': 'Priyanka Gandhi Vadra',
                'description': 'Updates on Priyanka Gandhi Vadra’s political activities.',
                'meta_title': 'Priyanka Gandhi Vadra News – BIGSTORY Network',
                'meta_description': 'Coverage of Priyanka Gandhi Vadra’s speeches and campaigns.',
                'meta_keywords': 'Priyanka Gandhi Vadra, Indian Politics, BIGSTORY Politics'
            },
            {
                'title': 'Yogi Adityanath',
                'description': 'Coverage of Yogi Adityanath’s governance and public statements.',
                'meta_title': 'Yogi Adityanath News – BIGSTORY Network',
                'meta_description': 'News on Yogi Adityanath’s policies and leadership in Uttar Pradesh.',
                'meta_keywords': 'Yogi Adityanath, Uttar Pradesh, BJP, BIGSTORY Politics'
            },

            # Parties & Institutions
            {
                'title': 'Bharatiya Janata Party',
                'description': 'News about the Bharatiya Janata Party in India.',
                'meta_title': 'BJP News – BIGSTORY Network',
                'meta_description': 'Coverage of Bharatiya Janata Party policies, leaders, and campaigns.',
                'meta_keywords': 'Bharatiya Janata Party, BJP, Indian Politics, BIGSTORY Politics'
            },
            {
                'title': 'Indian National Congress',
                'description': 'Coverage of the Indian National Congress party activities.',
                'meta_title': 'Indian National Congress News – BIGSTORY Network',
                'meta_description': 'Updates on INC policies, leadership, and political events.',
                'meta_keywords': 'Indian National Congress, INC, Indian Politics, BIGSTORY Politics'
            },
            {
                'title': 'Indian Parliament',
                'description': 'News and updates from the Indian Parliament.',
                'meta_title': 'Indian Parliament News – BIGSTORY Network',
                'meta_description': 'Coverage of parliamentary sessions, debates, and bills passed.',
                'meta_keywords': 'Indian Parliament, Lok Sabha, Rajya Sabha, BIGSTORY Politics'
            },
            {
                'title': 'Indian Government',
                'description': 'General coverage of the Indian central government.',
                'meta_title': 'Indian Government News – BIGSTORY Network',
                'meta_description': 'Reports on Indian government policies and decisions.',
                'meta_keywords': 'Indian Government, Politics, BIGSTORY India'
            },
            {
                'title': 'Opposition',
                'description': 'News about India’s political opposition parties.',
                'meta_title': 'Indian Opposition News – BIGSTORY Network',
                'meta_description': 'Coverage of opposition party statements, policies, and debates.',
                'meta_keywords': 'Opposition, Indian Politics, BIGSTORY Politics'
            },
        ]

        # States of India
        states = [
            'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh',
            'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jharkhand', 'Karnataka',
            'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Manipur', 'Meghalaya', 'Mizoram',
            'Nagaland', 'Odisha', 'Punjab', 'Rajasthan', 'Sikkim', 'Tamil Nadu', 'Telangana',
            'Tripura', 'Uttar Pradesh', 'Uttarakhand', 'West Bengal'
        ]

        for state in states:
            tags_data.append({
                'title': state,
                'description': f'Latest news and updates from {state}, India.',
                'meta_title': f'{state} News – BIGSTORY Network',
                'meta_description': f'Coverage of political, economic, and social news from {state}.',
                'meta_keywords': f'{state}, {state} News, India States, BIGSTORY Regional'
            })

        # Union Territories of India
        uts = [
            'Andaman and Nicobar Islands', 'Chandigarh', 'Dadra and Nagar Haveli and Daman and Diu',
            'Delhi', 'Jammu and Kashmir', 'Ladakh', 'Lakshadweep', 'Puducherry'
        ]

        for ut in uts:
            tags_data.append({
                'title': ut,
                'description': f'News and updates from {ut}, India.',
                'meta_title': f'{ut} News – BIGSTORY Network',
                'meta_description': f'Coverage of major news, events, and developments in {ut}.',
                'meta_keywords': f'{ut}, {ut} News, India Union Territories, BIGSTORY Regional'
            })

        # Create or update tags in DB
        for tag_data in tags_data:
            Tags.objects.update_or_create(
                title=tag_data['title'],
                defaults={
                    'description': tag_data['description'],
                    'meta_title': tag_data['meta_title'],
                    'meta_description': tag_data['meta_description'],
                    'meta_keywords': tag_data['meta_keywords'],
                }
            )

        self.stdout.write(self.style.SUCCESS('✅ Successfully inserted/updated political, state, and UT tags.'))
