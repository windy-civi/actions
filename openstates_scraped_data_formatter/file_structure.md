openstates-manifest-dev/
├── 📄 action.yml # GitHub Actions composite action
├── 📄 Pipfile # Python dependencies (pipenv)
├── 📄 Pipfile.lock # Locked dependencies
├── 📄 requirements.txt # Python dependencies (pip)
├── 📄 README.md # Project documentation
├── 📄 PROJECT_RULES.md # Data handling rules
├── 📄 .gitignore # Git ignore patterns
│
├── �� openstates_scraped_data_formatter/ # Main Python package
│ ├── 📄 main.py # Entry point for data processing
│ ├── 📄 extract_bill_text.py # CLI for bill text extraction
│ ├── �� analyze_state_data.py # State data analysis tool
│ ├── 📄 debug_extraction.py # Debug text extraction
│ ├── 📄 debug_metadata_structure.py # Debug metadata structure
│ ├── 📄 find_bills_with_urls.py # Find bills with URLs
│ │
│ ├── 📁 handlers/ # Data processing handlers
│ │ ├── 📄 bill.py # Bill data processing
│ │ ├── 📄 event.py # Event data processing
│ │ └── 📄 vote_event.py # Vote event processing
│ │
│ ├── 📁 postprocessors/ # Post-processing utilities
│ │ ├── 📄 event_bill_linker.py # Link events to bills
│ │ └── 📁 helpers/ # Helper functions
│ │ ├── 📄 **init**.py
│ │ ├── 📄 extract_bill_ids_from_event.py
│ │ ├── 📄 find_session_from_bill_id.py
│ │ ├── 📄 load_bill_to_session_mapping.py
│ │ └── 📄 run_handle_event.py
│ │
│ └── 📁 utils/ # Utility functions
│ ├── 📄 **init**.py
│ ├── 📄 file_utils.py # File operations
│ ├── 📄 interactive.py # Interactive utilities
│ ├── 📄 io_utils.py # I/O operations
│ ├── 📄 merge_session_log.py # Session log merging
│ ├── 📄 process_utils.py # Process utilities
│ ├── 📄 session_utils.py # Session utilities
│ ├── �� text_extraction.py # Bill text extraction (NEW!)
│ └── 📄 timestamp_tracker.py # Timestamp tracking
│
├── 📁 sample_data/ # Sample data for testing
│ ├── 📁 original/ # Original bill data
│ │ ├── �� bill_0001e018-6ccf-11f0-a587-065053629bd5.json
│ │ ├── �� bill_000bd828-7221-11f0-891a-76af6850676f.json
│ │ ├── �� bill_0010320c-6cd0-11f0-a587-065053629bd5.json
│ │ ├── �� bill_0011a5ec-6cd5-11f0-a587-065053629bd5.json
│ │ └── �� bill_0015d9fe-721c-11f0-891a-76af6850676f.json
│ │
│ ├── 📁 post_processing/ # Post-processed data
│ │ ├── 📄 metadata.json
│ │ ├── �� metadata (1).json
│ │ └── �� metadata (2).json
│ │
│ └── �� sample_state_data/ # State-specific sample data
│ ├── �� dc_20250306T050000Z_entire_bill.json
│ ├── 📄 dc2_20250102T050000Z_entire_bill.json
│ ├── �� il_20250123T000000Z_entire_bill.json
│ ├── 📄 il2_20241216T000000Z_entire_bill.json
│ ├── �� mn_20250210T000000Z_entire_bill.json
│ ├── 📄 mn2_20250609T000000Z_entire_bill.json
│ ├── �� tn_20241106T000000Z_entire_bill.json
│ └── �� wy_20250108T233509Z_entire_bill.json
│
└── 📁 .vscode/ # VS Code settings
└── 📄 settings.json

data_output/data_processed/country:us/state:wy/legislature/sessions/2025/bills/HB0128/
├── metadata.json
├── files/
│ ├── HB0128_Introduced.pdf # �� PRIMARY: Bill text
│ ├── HB0128_Introduced_extracted.txt # �� PRIMARY: Extracted bill text
│ └── documents/ # 🟡 SUPPORTING: Supporting materials
│ ├── HB0128_Fiscal_Note.pdf # �� SUPPORTING: Fiscal analysis
│ ├── HB0128_Fiscal_Note_extracted.txt # 🟡 SUPPORTING: Extracted fiscal text
│ ├── HB0128_Bill_Digest.pdf # 🟡 SUPPORTING: Bill summary
│ └── HB0128_Bill_Digest_extracted.txt # 🟡 SUPPORTING: Extracted digest text

data_output/data_processed/
├── 📁 country:us/ # Federal data
│ └── 📁 congress/
│ └── 📁 sessions/
│ └── 📁 119/
│ └── 📁 bills/
│ ├── 📁 HR1/
│ │ ├── 📄 metadata.json
│ │ ├── 📁 files/
│ │ │ ├── �� BILLS-119hr1ih_Introduced_in_House.xml
│ │ │ ├── �� BILLS-119hr1ih_Introduced_in_House_extracted.txt
│ │ │ ├── �� BILLS-119hr1eh_Engrossed_in_House.xml
│ │ │ └── �� BILLS-119hr1eh_Engrossed_in_House_extracted.txt
│ │ └── 📁 logs/
│ │ ├── 📄 20250103T050000Z_submitted_in_house.json
│ │ └── �� 20250115T060000Z_passed_house.json
│ └── 📁 S1234/
│ ├── 📄 metadata.json
│ └── 📁 files/
│ ├── 📄 BILLS-119s1234is_Introduced_in_Senate.xml
│ └── 📄 BILLS-119s1234is_Introduced_in_Senate_extracted.txt
│
├── 📁 country:us/state:wy/ # Wyoming state data
│ └── 📁 legislature/
│ └── 📁 sessions/
│ └── 📁 2025/
│ └── 📁 bills/
│ ├── 📁 HB0128/
│ │ ├── 📄 metadata.json
│ │ ├── 📁 files/
│ │ │ ├── 📄 HB0128_Introduced.pdf # �� PRIMARY: Bill text
│ │ │ ├── 📄 HB0128_Introduced_extracted.txt # �� PRIMARY: Extracted bill text
│ │ │ └── 📁 documents/ # 🟡 SUPPORTING: Supporting materials
│ │ │ ├── �� HB0128_Fiscal_Note.pdf # �� SUPPORTING: Fiscal analysis
│ │ │ ├── �� HB0128_Fiscal_Note_extracted.txt # 🟡 SUPPORTING: Extracted fiscal text
│ │ │ ├── �� HB0128_Bill_Digest.pdf # 🟡 SUPPORTING: Bill summary
│ │ │ └── �� HB0128_Bill_Digest_extracted.txt # 🟡 SUPPORTING: Extracted digest text
│ │ └── 📁 logs/
│ │ ├── �� 20250108T233509Z_bill_number_assigned.json
│ │ └── 📄 20250203T173256Z_introduced_and_referred.json
│ └── 📁 SF0018/
│ ├── 📄 metadata.json
│ └── 📁 files/
│ ├── 📄 SF0018_Introduced.pdf
│ └── 📄 SF0018_Introduced_extracted.txt
│
├── 📁 country:us/state:dc/ # DC data (with API key)
│ └── 📁 legislature/
│ └── 📁 sessions/
│ └── 📁 2025/
│ └── 📁 bills/
│ └── 📁 B25-0123/
│ ├── 📄 metadata.json
│ └── 📁 files/
│ ├── 📄 B25-0123_Introduced.pdf
│ └── 📄 B25-0123_Introduced_extracted.txt
│
└── 📁 country:us/state:il/ # Illinois state data
└── 📁 legislature/
└── 📁 sessions/
└── 📁 2025/
└── 📁 bills/
└── 📁 HB1234/
├── 📄 metadata.json
└── 📁 files/
├── 📄 HB1234_Introduced.html # HTML format
├── 📄 HB1234_Introduced_extracted.txt
└── 📁 documents/
├── �� HB1234_Fiscal_Note.pdf
└── �� HB1234_Fiscal_Note_extracted.txt
