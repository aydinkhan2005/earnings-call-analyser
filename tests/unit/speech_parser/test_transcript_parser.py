import pytest
import pandas as pd
import json
from pathlib import Path

from speech_parser import transcript_parser as tp


ROOT = Path(__file__).resolve().parents[3]


def test_normalize_company_name_rejects_non_string():
    with pytest.raises(TypeError):
        tp._normalize_company_name(123)


@pytest.mark.parametrize("bad_text", ["", "Q5 2016 Apple Inc Earnings Call", "hello world"])
def test_extract_header_metadata_rejects_missing_header_pattern(bad_text):
    with pytest.raises(ValueError, match="Could not locate header metadata"):
        tp._extract_header_metadata(bad_text)


def test_extract_header_metadata_rejects_non_string():
    with pytest.raises(TypeError):
        tp._extract_header_metadata(2024)


@pytest.mark.parametrize(
    "header_text, expected",
    [
        ("q2 2016 Apple Inc earnings call", ("Apple Inc", "2016", "2")),
        ("Q3 2020 L'Oréal Earnings Call", ("L'Oréal", "2020", "3")),
    ],
)
def test_extract_header_metadata_edge_cases_valid(header_text, expected):
    assert tp._extract_header_metadata(header_text) == expected


@pytest.mark.parametrize(
    "bad_header",
    [
        "Q2-2016 Apple Inc Earnings Call",
        "Quarter 2 2016 Apple Inc Earnings Call",
        "Q2 2016 Apple Inc",
    ],
)
def test_extract_header_metadata_edge_cases_invalid(bad_header):
    with pytest.raises(ValueError, match="Could not locate header metadata"):
        tp._extract_header_metadata(bad_header)


def test_extract_conference_participants_rejects_missing_line_column():
    with pytest.raises(KeyError):
        tp._extract_conference_participants(pd.DataFrame({"text": [" * Tim Cook"]}))


def test_extract_conference_participants_handles_empty_dataframe():
    assert tp._extract_conference_participants(pd.DataFrame(columns=["line"])) == []


def test_extract_corporate_participants_rejects_missing_line_column():
    with pytest.raises(KeyError):
        tp._extract_corporate_participants(pd.DataFrame({"text": ["Corporate Participants"]}))


def test_extract_corporate_participants_handles_empty_dataframe():
    assert tp._extract_corporate_participants(pd.DataFrame(columns=["line"])) == []


def test_extract_speaker_tuples_rejects_non_dataframe_input():
    with pytest.raises(TypeError):
        tp._extract_speaker_tuples([])


def test_extract_speaker_tuples_rejects_missing_line_column():
    with pytest.raises(KeyError):
        tp._extract_speaker_tuples(pd.DataFrame({"text": ["Operator [1]"]}))


def test_presentation_cutoff_handles_non_positive_total_speakers():
    assert tp._presentation_cutoff([1, 2], 0) == 0
    assert tp._presentation_cutoff([1, 2], -2) == 0


def test_presentation_cutoff_rejects_invalid_total_speakers_type():
    with pytest.raises(TypeError):
        tp._presentation_cutoff([1, 2], "2")


def test_presentation_cutoff_rejects_incompatible_marker_values():
    with pytest.raises(TypeError):
        tp._presentation_cutoff([1, "2"], 2)



def test_extract_corporate_participants_correctness_case_1():
    transcript_path = ROOT / "data/Transcripts/NVDA/2016-Aug-11-NVDA.txt"
    text = transcript_path.read_text(encoding="utf-8", errors="replace")
    transcript_df = pd.DataFrame({"line": text.splitlines()})

    expected_corporate = [
        ("Arnab Chanda", "NVIDIA Corporation", "VP of IR"),
        ("Jen-Hsun Huang", "NVIDIA Corporation", "President & CEO"),
        ("Colette Kress", "NVIDIA Corporation", "EVP & CFO")
    ]

    assert tp._extract_corporate_participants(transcript_df) == expected_corporate

def test_extract_corporate_participants_correctness_case_2():
    transcript_path = ROOT / "data/Transcripts/AAPL/2016-Apr-26-AAPL.txt"
    text = transcript_path.read_text(encoding="utf-8", errors="replace")
    transcript_df = pd.DataFrame({"line": text.splitlines()})

    expected_corporate = [
        ("Luca Maestri", "Apple Inc.", 'CFO'),
        ("Tim Cook", "Apple Inc.", 'CEO'),
        ("Nancy Paxton", 'Apple Inc.', 'Senior Director of IR')
    ]

    assert tp._extract_corporate_participants(transcript_df) == expected_corporate


def test_extract_conference_participants_correctness_case_1():
    transcript_path = ROOT / "data/Transcripts/NVDA/2016-Aug-11-NVDA.txt"
    text = transcript_path.read_text(encoding="utf-8", errors="replace")
    transcript_df = pd.DataFrame({"line": text.splitlines()})

    expected_conference = [
        ("Vijay Rakesh", "Mizuho Securities", "Analyst"),
        ("Steve  Smigie", "Raymond James", "Analyst"),
        ("Harlan Sur", "JPMorgan", "Analyst"),
        ("Blayne Curtis", "Barclays Capital", "Analyst"),
        ("C.J. Muse", "Evercore ISI", "Analyst"),
        ("Steven Chin", "UBS", "Analyst"),
        ("Craig Ellis", "B. Riley & Co.", "Analyst"),
        ("Vivek Arya", "BofA Merrill Lynch", "Analyst"),
        ("Mitch Steves", "RBC Capital Markets", "Analyst"),
        ("Kevin Cassidy", "Stifel Nicolaus", "Analyst"),
        ("Matt Ramsay", "Canaccord Genuity", "Analyst"),
        ("Joe Moore", "Morgan Stanley", "Analyst"),
        ("Rajvindra Gill", "Needham & Company", "Analyst"),
        ("Ambrish Srivastava", "BMO Capital Markets", "Analyst"),
        ("Mark Lipacis", "Jefferies LLC", "Analyst"),
        ("Ross Seymore", "Deutsche Bank", "Analyst"),
        ("Romit Shah", "Nomura Securities Co., Ltd.", "Analyst"),
        ("Brian Alger", "Raymond James", "Analyst"),
        ("Toshi Otani", "TransLink Capital", "Analyst"),
        ("Ian Ing", "MKM Partners", "Analyst"),
    ]

    assert tp._extract_conference_participants(transcript_df) == expected_conference


def test_extract_conference_participants_correctness_case_2():
    transcript_path = ROOT / "data/Transcripts/AMZN/2017-Apr-27-AMZN.txt"
    text = transcript_path.read_text(encoding="utf-8", errors="replace")
    transcript_df = pd.DataFrame({"line": text.splitlines()})

    expected_conference = [
        ("Heath P. Terry", "Goldman Sachs Group Inc., Research Division", "MD"),
        ("Ronald V. Josey", "JMP Securities LLC, Research Division", "MD and Senior Research Analyst"),
        ("Stephen D. Ju", "Credit Suisse AG, Research Division", "Director"),
        ("Eric James Sheridan", "UBS Investment Bank, Research Division", "MD and Equity Research Internet Analyst"),
        (
            "Gregory Scott Melich",
            "Evercore ISI, Research Division",
            "Senior MD, Head of Consumer Research Team and Senior Equity Research Analyst",
        ),
        ("Jason Stuart Helfstein", "Oppenheimer & Co. Inc., Research Division", "MD and Senior Internet Analyst"),
        ("Daniel Salmon", "BMO Capital Markets Equity Research", "Media and Internet Analyst"),
        ("Justin Post", "BofA Merrill Lynch, Research Division", "MD"),
        ("Brian Thomas Nowak", "Morgan Stanley, Research Division", "Research Analyst"),
        ("Douglas Till Anmuth", "JP Morgan Chase & Co, Research Division", "MD"),
        ("Mark S. Mahaney", "RBC Capital Markets, LLC, Research Division", "MD and Analyst"),
        ("Colin Alan Sebastian", "Robert W. Baird & Co. Incorporated, Research Division", "Senior Research Analyst"),
        ("Mark Alan May", "Citigroup Inc, Research Division", "Director and Senior Analyst"),
        ("Scott W. Devitt", "Stifel, Nicolaus & Company, Incorporated, Research Division", "MD"),
    ]

    assert tp._extract_conference_participants(transcript_df) == expected_conference


def test_extract_speaker_tuples_correctness_case_1():
    transcript_path = ROOT / "data/Transcripts/ASML/2016-Oct-19-ASML.txt"
    text = transcript_path.read_text(encoding="utf-8", errors="replace")
    transcript_df = pd.DataFrame({"line": text.splitlines()})

    expected_speaker_tuples = [
        ("Operator", "", ""),
        ("Craig DeYoung", "ASML Holdings NV", "VP IR & Corporate Communications"),
        ("Peter Wennink", "ASML Holdings NV", "President & CEO"),
        ("Wolfgang Nickl", "ASML Holdings NV", "EVP & CFO"),
        ("Peter Wennink", "ASML Holdings NV", "President & CEO"),
        ("Craig DeYoung", "ASML Holdings NV", "VP IR & Corporate Communications"),
        ("Operator", "", ""),
        ("Sandeep Deshpande", "JPMorgan", "Analyst"),
        ("Peter Wennink", "ASML Holdings NV", "President & CEO"),
        ("Sandeep Deshpande", "JPMorgan", "Analyst"),
        ("Peter Wennink", "ASML Holdings NV", "President & CEO"),
        ("Sandeep Deshpande", "JPMorgan", "Analyst"),
        ("Operator", "", ""),
        ("C.J. Muse", "Evercore ISI", "Analyst"),
        ("Wolfgang Nickl", "ASML Holdings NV", "EVP & CFO"),
        ("C.J. Muse", "Evercore ISI", "Analyst"),
        ("Peter Wennink", "ASML Holdings NV", "President & CEO"),
        ("C.J. Muse", "Evercore ISI", "Analyst"),
        ("Operator", "", ""),
        ("Kai Korschelt", "BofA Merrill Lynch", "Analyst"),
        ("Peter Wennink", "ASML Holdings NV", "President & CEO"),
        ("Kai Korschelt", "BofA Merrill Lynch", "Analyst"),
        ("Operator", "", ""),
        ("Timothy Arcuri", "Cowen and Company", "Analyst"),
        ("Wolfgang Nickl", "ASML Holdings NV", "EVP & CFO"),
        ("Timothy Arcuri", "Cowen and Company", "Analyst"),
        ("Wolfgang Nickl", "ASML Holdings NV", "EVP & CFO"),
        ("Timothy Arcuri", "Cowen and Company", "Analyst"),
        ("Operator", "", ""),
        ("Andrew Gardiner", "Barclays", "Analyst"),
        ("Peter Wennink", "ASML Holdings NV", "President & CEO"),
        ("Wolfgang Nickl", "ASML Holdings NV", "EVP & CFO"),
        ("Peter Wennink", "ASML Holdings NV", "President & CEO"),
        ("Andrew Gardiner", "Barclays", "Analyst"),
        ("Peter Wennink", "ASML Holdings NV", "President & CEO"),
        ("Andrew Gardiner", "Barclays", "Analyst"),
        ("Operator", "", ""),
        ("Gareth Jenkins", "UBS", "Analyst"),
        ("Wolfgang Nickl", "ASML Holdings NV", "EVP & CFO"),
        ("Peter Wennink", "ASML Holdings NV", "President & CEO"),
        ("Gareth Jenkins", "UBS", "Analyst"),
        ("Peter Wennink", "ASML Holdings NV", "President & CEO"),
        ("Wolfgang Nickl", "ASML Holdings NV", "EVP & CFO"),
        ("Gareth Jenkins", "UBS", "Analyst"),
        ("Operator", "", ""),
        ("Patrick Ho", "Stifel Nicolaus & Company, Inc.", "Analyst"),
        ("Peter Wennink", "ASML Holdings NV", "President & CEO"),
        ("Patrick Ho", "Stifel Nicolaus & Company, Inc.", "Analyst"),
        ("Peter Wennink", "ASML Holdings NV", "President & CEO"),
        ("Patrick Ho", "Stifel Nicolaus & Company, Inc.", "Analyst"),
        ("Operator", "", ""),
        ("Amit Ramchandani", "Citigroup", "Analyst"),
        ("Peter Wennink", "ASML Holdings NV", "President & CEO"),
        ("Wolfgang Nickl", "ASML Holdings NV", "EVP & CFO"),
        ("Amit Ramchandani", "Citigroup", "Analyst"),
        ("Wolfgang Nickl", "ASML Holdings NV", "EVP & CFO"),
        ("Peter Wennink", "ASML Holdings NV", "President & CEO"),
        ("Amit Ramchandani", "Citigroup", "Analyst"),
        ("Operator", "", ""),
        ("Farhan Ahmad", "Credit Suisse", "Analyst"),
        ("Peter Wennink", "ASML Holdings NV", "President & CEO"),
        ("Amit Ramchandani", "Citigroup", "Analyst"),
        ("Peter Wennink", "ASML Holdings NV", "President & CEO"),
        ("Amit Ramchandani", "Citigroup", "Analyst"),
        ("Craig DeYoung", "ASML Holdings NV", "VP IR & Corporate Communications"),
        ("Operator", "", ""),
        ("Francois Meunier", "Morgan Stanley", "Analyst"),
        ("Wolfgang Nickl", "ASML Holdings NV", "EVP & CFO"),
        ("Peter Wennink", "ASML Holdings NV", "President & CEO"),
        ("Francois Meunier", "Morgan Stanley", "Analyst"),
        ("Craig DeYoung", "ASML Holdings NV", "VP IR & Corporate Communications"),
        ("Operator", "", ""),
    ]
    expected_marker_numbers = [1, 2, 3, 4, 5] + list(range(1, 68))

    speaker_tuples, marker_numbers = tp._extract_speaker_tuples(transcript_df)

    assert speaker_tuples == expected_speaker_tuples
    assert marker_numbers == expected_marker_numbers


def test_extract_speaker_tuples_correctness_case_2():
    transcript_path = ROOT / "data/Transcripts/CSCO/2020-Aug-12-CSCO.txt"
    text = transcript_path.read_text(encoding="utf-8", errors="replace")
    transcript_df = pd.DataFrame({"line": text.splitlines()})

    expected_speaker_tuples = [
        ("Operator", "", ""),
        ("Marilyn Mora", "Cisco Systems, Inc.", "Director of Global IR"),
        ("Charles H. Robbins", "Cisco Systems, Inc.", "Chairman & CEO"),
        ("Kelly A. Kramer", "Cisco Systems, Inc.", "Executive VP & CFO"),
        ("Marilyn Mora", "Cisco Systems, Inc.", "Director of Global IR"),
        ("Operator", "", ""),
        ("Ahmed Sami Badri", "Crédit Suisse AG, Research Division", "Senior Analyst"),
        ("Charles H. Robbins", "Cisco Systems, Inc.", "Chairman & CEO"),
        ("Operator", "", ""),
        ("Meta A. Marshall", "Morgan Stanley, Research Division", "VP"),
        ("Charles H. Robbins", "Cisco Systems, Inc.", "Chairman & CEO"),
        ("Operator", "", ""),
        ("Ittai Kidron", "Oppenheimer & Co. Inc., Research Division", "MD"),
        ("Charles H. Robbins", "Cisco Systems, Inc.", "Chairman & CEO"),
        ("Operator", "", ""),
        ("James Dickey Suva", "Citigroup Inc., Research Division", "MD & Research Analyst"),
        ("Charles H. Robbins", "Cisco Systems, Inc.", "Chairman & CEO"),
        ("Kelly A. Kramer", "Cisco Systems, Inc.", "Executive VP & CFO"),
        ("James Dickey Suva", "Citigroup Inc., Research Division", "MD & Research Analyst"),
        ("Kelly A. Kramer", "Cisco Systems, Inc.", "Executive VP & CFO"),
        ("Operator", "", ""),
        ("Paul Jonas Silverstein", "Cowen and Company, LLC, Research Division", "MD & Senior Research Analyst"),
        ("Charles H. Robbins", "Cisco Systems, Inc.", "Chairman & CEO"),
        ("Kelly A. Kramer", "Cisco Systems, Inc.", "Executive VP & CFO"),
        ("Paul Jonas Silverstein", "Cowen and Company, LLC, Research Division", "MD & Senior Research Analyst"),
        ("Kelly A. Kramer", "Cisco Systems, Inc.", "Executive VP & CFO"),
        ("Operator", "", ""),
        ("Roderick B. Hall", "Goldman Sachs Group, Inc., Research Division", "MD"),
        ("Charles H. Robbins", "Cisco Systems, Inc.", "Chairman & CEO"),
        ("Kelly A. Kramer", "Cisco Systems, Inc.", "Executive VP & CFO"),
        ("Roderick B. Hall", "Goldman Sachs Group, Inc., Research Division", "MD"),
        ("Charles H. Robbins", "Cisco Systems, Inc.", "Chairman & CEO"),
        ("Marilyn Mora", "Cisco Systems, Inc.", "Director of Global IR"),
        ("Roderick B. Hall", "Goldman Sachs Group, Inc., Research Division", "MD"),
        ("Charles H. Robbins", "Cisco Systems, Inc.", "Chairman & CEO"),
        ("Operator", "", ""),
        ("Simon Matthew Leopold", "Raymond James & Associates, Inc., Research Division", "Research Analyst"),
        ("Kelly A. Kramer", "Cisco Systems, Inc.", "Executive VP & CFO"),
        ("Simon Matthew Leopold", "Raymond James & Associates, Inc., Research Division", "Research Analyst"),
        ("Charles H. Robbins", "Cisco Systems, Inc.", "Chairman & CEO"),
        ("Kelly A. Kramer", "Cisco Systems, Inc.", "Executive VP & CFO"),
        ("Charles H. Robbins", "Cisco Systems, Inc.", "Chairman & CEO"),
        ("Operator", "", ""),
        ("James Edward Fish", "Piper Sandler & Co., Research Division", "VP & Senior Research Analyst"),
        ("Kelly A. Kramer", "Cisco Systems, Inc.", "Executive VP & CFO"),
        ("James Edward Fish", "Piper Sandler & Co., Research Division", "VP & Senior Research Analyst"),
        ("Charles H. Robbins", "Cisco Systems, Inc.", "Chairman & CEO"),
        ("Kelly A. Kramer", "Cisco Systems, Inc.", "Executive VP & CFO"),
        ("James Edward Fish", "Piper Sandler & Co., Research Division", "VP & Senior Research Analyst"),
        ("Kelly A. Kramer", "Cisco Systems, Inc.", "Executive VP & CFO"),
        ("Operator", "", ""),
        ("Jeffrey Thomas Kvaal", "Wolfe Research, LLC", "Research Analyst"),
        ("Charles H. Robbins", "Cisco Systems, Inc.", "Chairman & CEO"),
        ("Kelly A. Kramer", "Cisco Systems, Inc.", "Executive VP & CFO"),
        ("Operator", "", ""),
        ("George Charles Notter", "Jefferies LLC, Research Division", "MD & Equity Research Analyst"),
        ("Charles H. Robbins", "Cisco Systems, Inc.", "Chairman & CEO"),
        ("Marilyn Mora", "Cisco Systems, Inc.", "Director of Global IR"),
        ("Charles H. Robbins", "Cisco Systems, Inc.", "Chairman & CEO"),
        ("Marilyn Mora", "Cisco Systems, Inc.", "Director of Global IR"),
        ("Operator", "", ""),
    ]
    expected_marker_numbers = [1, 2, 3, 4, 5] + list(range(1, 57))

    speaker_tuples, marker_numbers = tp._extract_speaker_tuples(transcript_df)

    assert speaker_tuples == expected_speaker_tuples
    assert marker_numbers == expected_marker_numbers
